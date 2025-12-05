# amazon_client.py – DIRETTO GRATIS 2025 – PRENDE SOLO OFFERTE REALI
import requests
from bs4 import BeautifulSoup
import random
import time
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def get_offers(max_items=8):
    urls = [
        "https://www.amazon.it/gp/goldbox",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/s?k=offerte+del+giorno"
    ]

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        ]),
        "Accept-Language": "it-IT,it;q=0.9",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    offers = []
    session = requests.Session()
    session.headers.update(headers)

    for url in urls:
        try:
            time.sleep(random.uniform(3, 6))
            r = session.get(url, timeout=40)

            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.content, "lxml")

            # Selettori per offerte reali (2025, evita placeholder)
            cards = soup.find_all("div", {"data-asin": True})[:20]

            for card in cards:
                a = card.find("a", href=True)
                if not a:
                    continue

                raw_url = a["href"]
                if not raw_url.startswith("http"):
                    raw_url = "https://www.amazon.it" + raw_url
                full_url = add_affiliate_tag(raw_url)

                title_elem = card.find("h2") or card.find("span", class_="a-size-base-plus")
                title = title_elem.get_text(strip=True) if title_elem else None
                if not title or len(title) < 20 or title.startswith("Offerta Amazon"):  # FILTRA MERDA
                    continue

                price_elem = card.find("span", class_="a-offscreen") or card.find("span", class_="a-price-whole")
                price = price_elem.get_text(strip=True) if price_elem else "Scopri prezzo"

                img = card.find("img")
                image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300?text=Deal"

                offers.append({
                    "title": title,
                    "url": full_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })
                logging.info(f"OFFERTA REALE: {title[:50]}... {price}")

                if len(offers) >= max_items:
                    break

        except Exception as e:
            logging.error(f"Errore: {e}")

    logging.info(f"TROVATE {len(offers)} offerte reali – POSTO ORA!")
    return offers
