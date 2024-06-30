import os
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import datetime
from avrupada_karavan.models import Product, Category, Brand, ProductImage
import requests


class Command(BaseCommand):
    help = 'Import data from Excel file to Django database'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')



    def handle(self, *args, **options):
        excel_file = options['excel_file']
        df = pd.read_excel(excel_file)

        def translate_text(text, target='tr'):
            url = "https://translation.googleapis.com/language/translate/v2"

            params = {
                'q': text,
                'target': target,
                'key': os.environ.get('GD_API')
            }

            response = requests.get(url, params=params)

            if response.status_code == 200:
                result = response.json()
                translated_text = result['data']['translations'][0]['translatedText']
                print("Text: {}".format(text))
                print("Translation: {}".format(translated_text))
                return translated_text
            else:
                print(f"Error: {response.status_code}, {response.text}")
                return None


        def clean_value(value, default=0):
            try:
                return int(
                    str(value).replace('\xa0', '').replace('km', '').replace('kg', '').replace('€', '').replace('£',
                                                                                                                '').replace(
                        '$', '').replace(' ', '').replace('.', '').replace(',', '.'))
            except (ValueError, TypeError):
                return default

        def clean_price(value):
            try:
                value = str(value).replace('\xa0', '').replace('€', '').replace('(Brutto)','').strip()
                value = value.replace('.', '').replace(',', '.')
                price_numeric = Decimal(value) * 34  # Euro to TL conversion
                return price_numeric
            except (ValueError, TypeError, InvalidOperation):
                return Decimal("0.00")

        def clean_date(value, default_year=2024):
            try:
                return datetime.strptime(value, '%m/%Y').date()
            except (ValueError, TypeError):
                return datetime(default_year, 1, 1).date()

        def download_image(image_url, folder='product_images/'):
            try:
                if 'https://' not in image_url:
                    image_url = 'https://' + image_url

                # Remove existing rule parameter if present
                if '?rule' in image_url:
                    image_url = image_url.split('?rule=')[0]

                # Add the 1024px rule
                download_url = f"{image_url}?rule=mo-1024.jpg"

                response = requests.get(download_url)
                response.raise_for_status()

                # Use the original filename without parameters for storing
                image_name = os.path.basename(image_url)

                image = Image.open(BytesIO(response.content))
                image_io = BytesIO()
                image.save(image_io, format=image.format)
                return ContentFile(image_io.getvalue(), name=image_name)
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Failed to download image from : {e}'))
                return None

        def generate_description(row, attributes):
            description_template = (
                "Bu ilanın markası {brand}. Kişi kapasitesi {number_of_sleeping_places}. "
                "Fiyatı {price} TL olan bu araç, {mileage} km mesafededir ve {transmission} şanzımana sahiptir. "
                "Kayıt tarihi {registration_date} olup, motor gücü {power} dir. "
                "Yakıt türü {fuel_type}, rengi {color}, {axles} akslı ve izin verilen toplam ağırlığı {permissible_gross_weight} kg'dir."
            )
            return description_template.format(
                brand=row['Title'].split()[0],
                number_of_sleeping_places=attributes.get('numberOfBunks', 'N/A'),
                price=clean_price(row['Price']),
                mileage=clean_value(attributes.get('mileage', '0').split()[0]),
                transmission=attributes.get('transmission', 'N/A'),
                registration_date=attributes.get('firstRegistration', 'N/A'),
                power=attributes.get('power', 'N/A'),
                fuel_type=attributes.get('fuel', 'N/A'),
                color=attributes.get('color', 'N/A'),
                axles=attributes.get('axles', 'N/A'),
                permissible_gross_weight=clean_value(attributes.get('licensedWeight', '0').split()[0])
            )


        for _, row in df.iterrows():
            attributes = eval(row['Attributes']) if pd.notna(row['Attributes']) else {}
            # Parse features
            features = translate_text(row['Features'].strip('[]').replace("'", "")).split(', ') if pd.notna(row['Features']) else []
            if len(features) > 3:

                # Get or create Category from attributes
                category_name = translate_text(attributes.get('category', 'Default Category'))
                category, _ = Category.objects.get_or_create(name=category_name)

                # Get or create Brand from the first word of the title
                brand_name = row['Title'].split()[0]
                brand, _ = Brand.objects.get_or_create(
                    name=brand_name,
                    defaults={'founded_year': datetime.now().year}
                )
                description = row['Description']
                if len(description) < 4 or description is None:
                    description = generate_description(row, attributes)
                description = translate_text(description)
                if description is None:
                    description = row['Title']

                try:
                    # Create Product
                    product = Product.objects.create(
                        category=category,
                        brand=brand,
                        title=translate_text(row['Title'].replace('*', '')),
                        price=clean_price(row['Price']),
                        description=translate_text(description),
                        features=features,
                        mileage=clean_value(attributes.get('mileage', '0').split()[0]),
                        power=attributes.get('power', '').replace('\xa0', ' '),
                        fuel_type=translate_text(attributes.get('fuel', '')),
                        transmission=translate_text(attributes.get('transmission', '')),
                        emission_class=attributes.get('emissionClass', ''),
                        emission_sticker=translate_text(attributes.get('emissionsSticker', '')),
                        registration_date=clean_date(attributes.get('firstRegistration', '01/2000')),
                        number_of_owners=int(attributes.get('numberOfPreviousOwners', 1)),
                        permissible_gross_weight=clean_value(attributes.get('licensedWeight', '0').split()[0]),
                        HU=datetime.now().date() if attributes.get('hu') == 'Neu' else None,
                        air_conditioning=translate_text(attributes.get('climatisation', '')),
                        parking_assists=translate_text(attributes.get('parkAssists', '')),
                        color=translate_text(attributes.get('color', '')),
                        axles=int(attributes.get('axles', 2)),
                        number_of_sleeping_places=int(attributes.get('numberOfBunks', 2)),
                        vehicle_length=clean_value(attributes.get('vehicleLength', '0').split()[0]),
                        vehicle_width=clean_value(attributes.get('vehicleWidth', '0').split()[0]),
                        vehicle_height=clean_value(attributes.get('vehicleHeight', '0').split()[0]),
                        bed_types=translate_text(attributes.get('bedTypes', '')),
                        seating_groups=translate_text(attributes.get('seatingGroups', '')),
                        url=row.get('Url', ''),
                        attributes=attributes
                    )
                    # Create ProductImages
                    images = row['Images'].strip('[]').replace("'", "").split(', ') if pd.notna(row['Images']) else []
                    for image_url in images:
                        image_url = image_url.strip()  # Remove any leading/trailing whitespace
                        if image_url:  # Only process non-empty URLs
                            image_file = download_image(image_url)
                            if image_file:
                                ProductImage.objects.create(product=product, image=image_file)
                except:
                    pass

                self.stdout.write(self.style.SUCCESS(f'Successfully imported product: {product.title}'))
