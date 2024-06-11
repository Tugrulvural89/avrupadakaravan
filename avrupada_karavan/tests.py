from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from decimal import Decimal, InvalidOperation
import json
import time
import pandas as pd
from googletrans import Translator
import random




def translate_text(text, src='de', dest='tr'):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        return f"Çeviri hatası: {e}"


def random_wait(min_wait=1, max_wait=3):
    time.sleep(random.uniform(min_wait, max_wait))


def move_mouse_like_human(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    random_wait(0.5, 1.5)
    actions.click(element).perform()


options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-data-dir=/Users/kasimtugrulvural/Library/Application Support/Google/Chrome/Profile 1")

service = ChromeService(
    executable_path='/Users/kasimtugrulvural/downloads/chromedriver')

driver = webdriver.Chrome(service=service, options=options)

driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    """
})

data = []

try:
    base_url = 'https://suchen.mobile.de/fahrzeuge/search.html?cn=DE&gn=Essen%2C+Nordrhein-Westfalen&isSearchRequest=true&ll=51.451832%2C7.01063&rd=10&ref=srp&refId=539e3acc-5b0b-32f3-2529-9f8c7acf3e13&s=Motorhome&sb=rel&vc=Motorhome'

    for page_num in range(1, 14):
        print(f"Scraping page {page_num}")
        url = f"{base_url}&pageNumber={page_num}"
        driver.get(url)
        random_wait(3, 5)

        script = '''
        return window.__INITIAL_STATE__.search.srp.data.searchResults.items;
        '''
        items = driver.execute_script(script)

        for item in items:
            title = item.get('title', 'No title')
            translated_title = translate_text(title)
            brand = title.split(' ')[0] if title else 'No brand'
            price_euro = item.get('price', {}).get('gross', 0)
            price_tl = price_euro
            url = item.get('relativeUrl', 'No URL')
            main_image = item.get('previewImage', {}).get('src', 'No main image')
            contact_phone = item.get('contactInfo', {}).get('contactPhone', 'No contact phone')
            seller_name = item.get('contactInfo', {}).get('name', 'No seller name')
            category = translate_text(item.get('category', 'No category'))
            seller_location = item.get('contactInfo', {}).get('location', 'No seller location')

            images = [main_image]
            if 'previewThumbnails' in item:
                images.extend([thumbnail.get('src', 'No image') for thumbnail in item['previewThumbnails']])

            attributes = item.get('attr', {})

            translated_attributes = {}
            for attr_key, attr_value in attributes.items():
                if attr_value is None:
                    translated_attributes[attr_key] = 'No data'
                else:
                    if attr_key == 'loc':
                        translated_attributes[attr_key] = attr_value
                    else:
                        translated_attributes[attr_key] = translate_text(attr_value)

            if len(translated_title) < 15:
                additional_info = []
                if 'category' in item and item['category']:
                    additional_info.append(translate_text(item['category']))
                if 'tr' in translated_attributes and translated_attributes['tr']:
                    additional_info.append(translated_attributes['tr'])
                if 'pw' in translated_attributes and translated_attributes['pw']:
                    additional_info.append(translated_attributes['pw'])
                if 'ml' in translated_attributes and translated_attributes['ml']:
                    additional_info.append(f"{translated_attributes['ml']} km")
                translated_title += " " + " ".join(additional_info)

            data.append({
                'Title': translated_title,
                'Brand': brand,
                'Price': price_tl,
                'URL': f"https://suchen.mobile.de{url}",
                'Main Image': main_image,
                'Images': ', '.join(images),
                'Contact Phone': contact_phone,
                'Seller Name': seller_name,
                'Seller Location': seller_location,
                'Category': category,
                **translated_attributes
            })

    print(f"Total items scraped: {len(data)}")


finally:
    driver.quit()

df = pd.DataFrame(data)
print(df.head())  # Print first few rows to ensure DataFrame is correct
df.to_excel('vehicle_data.xlsx', index=False)
print("Data saved to vehicle_data.xlsx")
