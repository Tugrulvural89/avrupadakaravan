import os
import requests
from io import BytesIO
from PIL import Image
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from avrupada_karavan.models import Category, Brand, Product, ProductImage
import datetime

class Command(BaseCommand):
    help = 'Import vehicle data from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='The file path of the Excel file to import',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        if not file_path:
            self.stdout.write(self.style.ERROR('Please provide the file path using --file'))
            return

        # Load the cleaned Excel file
        df = pd.read_excel(file_path)

        # Check for required columns
        required_columns = [
            'Title', 'Brand', 'Price', 'ml', 'tr', 'yc', 'pw', 'ft', 'lw', 'c',
            'ecol', 'ax', 'Contact Phone', 'Seller Name', 'Seller Location',
            'URL', 'Images'
        ]

        for col in required_columns:
            if col not in df.columns:
                self.stdout.write(self.style.ERROR(f'Missing required column: {col}'))
                return

        df.fillna('', inplace=True)  # Fill missing values with empty string

        def clean_value(value, default=0):
            try:
                return int(
                    str(value).replace('\xa0', '').replace('km', '').replace('kg', '').replace('€', '').replace('£', '').replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
                )
            except (ValueError, TypeError):
                return default

        def clean_price(value):
            try:
                # Remove non-numeric characters except for commas and periods
                value = str(value).replace('\xa0', '').replace('€', '').strip()
                # Replace comma with period to handle European decimal format
                value = value.replace('.', '').replace(',', '.')
                price_numeric = Decimal(value) * 34  # Euro to TL conversion
                return price_numeric
            except (ValueError, TypeError, InvalidOperation):
                return Decimal("0.00")

        def clean_date(value, default_year=2024):
            try:
                return datetime.date.fromisoformat(str(value))
            except (ValueError, TypeError):
                return datetime.date(default_year, 1, 1)  # Default to January 1st of the default year

        def download_image(image_url, folder='product_images/'):
            try:
                response = requests.get(image_url)
                response.raise_for_status()
                image_name = os.path.basename(image_url.split('?')[0])
                image = Image.open(BytesIO(response.content))
                image_io = BytesIO()
                image.save(image_io, format=image.format)
                return ContentFile(image_io.getvalue(), name=image_name)
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Failed to download image from {image_url}: {e}'))
                return None

        def generate_description(row):
            description_template = (
                "Bu ilanın markası {brand}. Kişi kapasitesi {number_of_sleeping_places}. "
                "Fiyatı {price} TL olan bu araç, {mileage} km mesafededir ve {transmission} şanzımana sahiptir. "
                "Kayıt tarihi {registration_date} olup, motor gücü {power} kW (hp) dir. "
                "Yakıt türü {fuel_type}, rengi {color}, {axles} akslı ve izin verilen toplam ağırlığı {permissible_gross_weight} kg'dir."
            )
            return description_template.format(
                brand=row.get('Brand', 'N/A'),
                number_of_sleeping_places=clean_value(row.get('z', 2), 2),
                price=clean_price(row.get('Price', '0')),
                mileage=clean_value(row.get('ml', 0)),
                transmission=row.get('tr', 'N/A'),
                registration_date=clean_date(row.get('yc', '2024-01-01')),
                power=row.get('pw', 'N/A'),
                fuel_type=row.get('ft', 'N/A'),
                color=row.get('ecol', 'N/A'),
                axles=clean_value(row.get('ax', 2), 2),
                permissible_gross_weight=clean_value(row.get('lw', 0))
            )

        for _, row in df.iterrows():
            # Create or get the brand
            brand, created = Brand.objects.get_or_create(name=row['Brand'], founded_year=2024)

            # Create or get the category
            category, created = Category.objects.get_or_create(name=row['Category'])

            # Generate description
            description = generate_description(row)

            product = Product(
                category=category,
                brand=brand,
                title=row.get('Title', 'N/A'),
                description=description,
                price=clean_price(row.get('Price', '0')),
                mileage=clean_value(row.get('ml', 0)),
                transmission=row.get('tr', 'N/A'),
                registration_date=clean_date(row.get('yc', '2024-01-01')),
                power=row.get('pw', 'N/A'),
                fuel_type=row.get('ft', 'N/A'),
                number_of_owners=1,
                permissible_gross_weight=clean_value(row.get('lw', 0)),
                HU=clean_date(row.get('eu', '2024-01-01')),
                air_conditioning=row.get('c', 'N/A'),
                color=row.get('ecol', 'N/A'),
                axles=clean_value(row.get('ax', 2), 2),
                number_of_sleeping_places=clean_value(row.get('z', 2), 2),
                url=row.get('URL', 'N/A'),
            )
            product.save()

            # Create product images
            image_urls = row.get('Images', '').split(', ')
            for image_url in image_urls:
                image_file = download_image(image_url)
                if image_file:
                    ProductImage.objects.create(product=product, image=image_file)

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))
