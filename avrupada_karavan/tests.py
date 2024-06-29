from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
import json
import time
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def random_wait(min_wait, max_wait):
    time.sleep(random.uniform(min_wait, max_wait))


def move_mouse_like_human(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(element, random.randint(1, 5), random.randint(1, 5))
    actions.move_by_offset(random.randint(-5, 5), random.randint(-5, 5))
    actions.click()
    actions.perform()
    random_wait(0.5, 1.5)


def scroll_to_bottom(driver):
    driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")
    random_wait(5, 8)


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    proxies = []
    for row in soup.find("table", attrs={"class": "table table-striped table-bordered"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            proxies.append(f"{ip}:{port}")
        except IndexError:
            continue
    return proxies


proxy_list = get_free_proxies()
print(f"{len(proxy_list)} adet proxy bulundu.")
print("İlk 5 proxy:")
for proxy in proxy_list[:5]:
    print(proxy)


def get_random_proxy():
    return random.choice(proxy_list)


def create_driver():
    ua = UserAgent(browsers=['chrome'], os=['macos'])
    user_agent = ua.random

    options = webdriver.ChromeOptions()
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    #options.add_argument(f'--proxy-server={get_random_proxy()}')

    options.add_argument("user-data-dir=/Users/kasimtugrulvural/Library/Application Support/Google/Chrome/Profile 2")


    service = ChromeService(executable_path='/Users/kasimtugrulvural/downloads/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    return driver


def scrape_data(base_url, num_pages):
    data = []
    driver = create_driver()

    try:
        for page_num in range(1, num_pages + 1):
            print(f"Scraping page {page_num}")
            url = f"{base_url}&pageNumber={page_num}"
            driver.get(url)
            random_wait(10, 15)

            script = 'return window.__INITIAL_STATE__.search.srp.data.searchResults.items;'
            items = driver.execute_script(script)
            scroll_to_bottom(driver)

            for item in items:
                url = item.get('relativeUrl', 'No URL')
                if url != 'No URL':
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    id_value = query_params.get('id', [''])[0]

                    new_url = f'https://suchen.mobile.de/fahrzeuge/printView.html?id={id_value}'
                    random_wait(3, 5)
                    driver.get(new_url)
                    random_wait(4, 5)
                    scroll_to_bottom(driver)
                    random_wait(2, 3)

                    try:
                        features_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, "features"))
                        )
                        feature_items = features_element.find_elements(By.XPATH, ".//div[@class='g-col-4']/p")
                        features = [item.text for item in feature_items]
                    except Exception as e:
                        features = []
                        print(f"Error fetching features: {e}")

                    try:
                        description_elem = driver.find_element(By.XPATH,
                                                               '//*[@id="print"]/div[2]/div/div[4]/div/div[2]/div/div/div')
                        description = description_elem.text.strip()
                    except Exception as e:
                        description = ""
                        print(f"Error fetching description: {e}")

                    try:
                        div_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div.g-col-8"))
                        )

                        link_element = div_element.find_element(By.CSS_SELECTOR, "a.link--no-decoration")
                        random_wait(1, 3)
                        driver.execute_script("arguments[0].setAttribute('target', '_self')", link_element)
                        link_element.click()

                        WebDriverWait(driver, 10).until(EC.staleness_of(div_element))
                        random_wait(4, 7)
                        print(f"Başarıyla tıklandı ve yönlendirildi: {driver.current_url}")

                        try:
                            WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//script[contains(text(), 'window.__INITIAL_STATE__')]"))
                            )

                            time.sleep(5)

                            script = 'return JSON.stringify(window.__INITIAL_STATE__);'
                            initial_state_json = driver.execute_script(script)

                            if initial_state_json:
                                initial_state = json.loads(initial_state_json)
                                ad_data = initial_state.get('ad', {})

                                if ad_data:
                                    ad_id = ad_data.get('id', 'ad_id not found')
                                    price = ad_data.get('price', 'Price not found')
                                    title = ad_data.get('title', 'Title not found')
                                    images = [img.get('uri', '') for img in ad_data.get('images', [])]
                                    attributes = ad_data.get('attributes', {})
                                    data.append({
                                        'ID': ad_id,
                                        'Title': title,
                                        'Price': price,
                                        'Description': description,
                                        'Features': features,
                                        'Images': images,
                                        'Attributes': attributes,
                                        'Url': new_url
                                    })
                                    print(ad_id, title, price , len(features), len(images), len(attributes), new_url)
                                else:
                                    print(f"Ad data for ID {id_value} could not be found in the expected structure.")
                            else:
                                print("window.__INITIAL_STATE__ objesi bulunamadı.")
                        except Exception as e:
                            print(f"Hata oluştu: {str(e)}")
                    except Exception as e:
                        print(f"Hata oluştu: {str(e)}")

            if page_num % 3 == 0:
                print("Yeni oturum başlatılıyor...")
                driver.quit()
                driver = create_driver()
                random_wait(30, 60)

    finally:
        driver.quit()

    return data


# Ana program
base_url = 'https://suchen.mobile.de/fahrzeuge/search.html?cn=DE&gn=Essen%2C+Nordrhein-Westfalen&isSearchRequest=true&ll=51.451832%2C7.01063&rd=10&ref=srp&refId=539e3acc-5b0b-32f3-2529-9f8c7acf3e13&s=Motorhome&sb=rel&vc=Motorhome'
num_pages = 1

data = scrape_data(base_url, num_pages)

df = pd.DataFrame(data)
print(df.head())
df.to_excel('vehicle_data.xlsx', index=False)
print("Data saved to vehicle_data.xlsx")