# amazon_client.py – SELENIUM HEADLESS 2025 – CARICA JS E SPACCA BLOCCO
import random
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from config import AMAZON_ASSOC_TAG

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def setup_driver():
    options = Options()
    options.add_argument("--headless")  # no GUI su server
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_offers(keywords="offerte del giorno", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno&i=deals"
    ]

    offers = []
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)

    for url in urls:
        try:
            logging.info(f"Carico con Selenium: {url}")
            driver.get(url)
            time.sleep(random.uniform(3, 6))  # tempo per JS

            # Aspetta che carichino i deals
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-asin], .s-result-item, div[data-component-type='s-search-result']")))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            cards = soup.select("div[data-asin], .s-result-item, [cel_widget_id*='DEAL'], div.octopus-pc-item")[:20]

            for card in cards:
                a_tag = card.find("a", href=True)
                if not a_tag:
                    continue
                raw_url = a_tag["href"]
                if not raw_url.startswith("http"):
                    raw_url = "https://www.amazon.it" + raw_url
                full_url = add_affiliate_tag(raw_url)

                title_elem = card.find("h2") or card.find("span", class_="a-size-base-plus") or card.find("a")
                title = title_elem.get_text(strip=True)[:150] if title_elem else "Offerta Amazon"

                if len(title) < 10:
                    continue

                price_elem = card.find("span", class_="a-price-whole") or card.find("span", class_="a-offscreen")
                price = price_elem.get_text(strip=True) if price_elem else "Vedi deal"

                img_elem = card.find("img")
                image = img_elem["src"] if img_elem and img_elem.get("src") else "https://via.placeholder.com/300?text=Amazon+Deal"

                offers.append({
                    "title": title,
                    "url": full_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })
                logging.info(f"Trovata: {title[:50]}...")

                if len(offers) >= max_items:
                    logging.info(f"SPARATE {len(offers)} offerte da {url}!")
                    break

        except Exception as e:
            logging.error(f"Selenium errore su {url}: {e}")
        finally:
            if len(offers) >= max_items:
                break

    driver.quit()
    return offers[:max_items]
