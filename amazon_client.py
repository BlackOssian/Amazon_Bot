# amazon_client.py – NO PROXY DIRETTO – VERSIONE SEMPLICE E FUNZIONANTE 2025
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def get_offers(keywords="offerte del giorno", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno",
        "https://www.amazon.it/offerte-del-giorno"  # URL alternativo per fallback
    ]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
    ]

    offers = []
    session = requests.Session()

    for attempt in range(3):  # 3 tentativi con headers diversi
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": "it-IT,it;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        session.headers.update(headers)
        logging.info(f"Tentativo diretto {attempt+1}/3 con User-Agent diverso...")

        for url in urls:
            try:
                time.sleep(random.uniform(2, 5))
                r = session.get(url, timeout=30)

                if r.status_code != 200 or len(r.text) < 10000:
                    logging.warning(f"Bloccato su {url} (status: {r.status_code})")
                    continue

                soup = BeautifulSoup(r.content, "lxml")
                cards = soup.select("div[data-asin]") or soup.select(".s-result-item") or soup.select("div.a-cardui")

                if not cards:
                    logging.warning(f"Nessuna card trovata su {url}")
                    continue

                for card in cards[:15]:
                    a_tag = card.find("a", href=True)
                    if not a_tag:
                        continue
                    raw_url = a_tag["href"]
                    if not raw_url.startswith("http"):
                        raw_url = "https://www.amazon.it" + raw_url
                    full_url = add_affiliate_tag(raw_url)

                    title_elem = card.find("h2") or card.find("span", class_="a-size-base-plus")
                    title = title_elem.get_text(strip=True)[:150] if title_elem else "Offerta Amazon"

                    if len(title) < 10:
                        continue

                    price_elem = card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")
                    price = price_elem.get_text(strip=True) if price_elem else "Scopri prezzo"

                    img_elem = card.find("img")
                    image = img_elem["src"] if img_elem and img_elem.get("src") else "https://via.placeholder.com/300?text=Amazon+Deal"

                    offers.append({
                        "title": title,
                        "url": full_url,
                        "image": image,
                        "price": price,
                        "currency": "€"
                    })
                    logging.info(f"Trovata diretta: {title[:50]}... {price}")

                if len(offers) >= max_items:
                    logging.info(f"BOOM DIRETTO! {len(offers)} offerte trovate!")
                    return offers

            except Exception as e:
                logging.error(f"Errore diretto su {url}: {e}")

    logging.warning("Zero offerte stavolta, ma riprovo tra 4 ore – Amazon stronzo!")
    return offers
