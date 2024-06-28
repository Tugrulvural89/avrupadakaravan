from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from decimal import Decimal, InvalidOperation
import json
import time
import pandas as pd
import random
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

def random_wait(min_wait, max_wait):
    time.sleep(random.uniform(min_wait, max_wait))


def move_mouse_like_human(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    random_wait(0.5, 1.5)
    actions.click(element).perform()

def scroll_to_bottom(driver):
    driver.execute_script("""
        window.scrollTo({
            top: document.body.scrollHeight,
            behavior: 'smooth'
        });
    """)
    random_wait(3, 5)

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
    for page_num in range(1, 2):
        print(f"Scraping page {page_num}")
        url = f"{base_url}&pageNumber={page_num}"
        driver.get(url)
        random_wait(3, 5)

        script = '''
        return window.__INITIAL_STATE__.search.srp.data.searchResults.items;
        '''
        items = driver.execute_script(script)
        scroll_to_bottom(driver)
        for item in items:
            url = item.get('relativeUrl', 'No URL')
            if url != 'No URL':
                # URL'den ID'yi çıkar

                parsed_url = urlparse(url)
                query_params = parse_qs(parsed_url.query)
                id_value = query_params.get('id', [''])[0]  # ID parametresini al, yoksa boş string döndür

                # Yeni URL oluştur
                new_url = f'https://suchen.mobile.de/fahrzeuge/printView.html?id={id_value}'
                random_wait(3,5)
                # Yeni URL'yi ziyaret et
                driver.get(new_url)
                random_wait(4,5)
                scroll_to_bottom(driver)

                random_wait(2,3)

                try:
                    # Belirtilen div elementini bul
                    div_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.g-col-8"))
                    )

                    # Div içindeki link elementini bul
                    link_element = div_element.find_element(By.CSS_SELECTOR, "a.link--no-decoration")
                    random_wait(1, 2)
                    # Link elementinin target özelliğini _self olarak değiştir
                    driver.execute_script("arguments[0].setAttribute('target', '_self')", link_element)

                    # Linke tıkla
                    link_element.click()

                    # Yeni sayfanın yüklenmesini bekle
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(div_element)
                    )
                    random_wait(2, 4)
                    print(f"Başarıyla tıklandı ve yönlendirildi: {driver.current_url}")

                except Exception as e:
                    print(f"Hata oluştu: {str(e)}")

    print(f"Total items scraped: {len(data)}")

finally:
    driver.quit()

#df = pd.DataFrame(data)
#print(df.head())  # Print first few rows to ensure DataFrame is correct
#df.to_excel('vehicle_data.xlsx', index=False)
print("Data saved to vehicle_data.xlsx")
