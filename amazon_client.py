# amazon_client.py – versione 2025 che fotte Amazon
import requests
from bs4 import BeautifulSoup
import random
import logging

AMAZON_ASSOC_TAG = "darkitalia-21"

def add_affiliate_tag(url):
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}tag={AMAZON_ASSOC_TAG}"

def get_offers(keywords="", max_items=10):
    urls = [
        "https://www.amazon.it/gp/goldbox/",
        "https://www.amazon.it/deals",
        "https://www.amazon.it/offerte-del-giorno",
    ]

    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36",
        ]),
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    session = requests.Session()
    session.headers.update(headers)

    offers = []

    for url in urls:
        try:
            logging.info(f"Provo URL: {url}")
            r = session.get(url, timeout=20)
            if r.status_code != 200:
                continue

            soup = BeautifulSoup(r.content, "html.parser")

            # Amazon usa mille classi diverse, prendiamo tutto quello che assomiglia a un deal
            cards = soup.select('[data-asin]') or soup.select('.octopus-pc-item') or soup.select('[cel_widget_id*="DEAL"]') or soup.find_all("div", {"id": lambda x: x and "dealCard" in x})

            for card in cards[:30]:
                link = card.find("a", class_="a-link-normal") or card.find("a")
                if not link or not link.get("href"):
                    continue

                raw_url = link["href"]
                if not raw_url.startswith("http"):
                    raw_url = "https://www.amazon.it" + raw_url.split("?")[0]

                title = (card.find("span", {"id": lambda x: x and "dealTitle" in x}) or
                         card.find("h2") or
                         card.find("div", class_="a-row") or
                         card).get_text(strip=True)[:200]

                price_span = card.find("span", class_="a-price-whole") or card.find("span", class_="a-offscreen")
                price = price_span.get_text(strip=True) if price_span else "N/D"

                img = card.find("img")
                image = img["src"] if img and img.get("src") else "https://via.placeholder.com/300x300"

                final_url = add_affiliate_tag(raw_url)

                offers.append({
                    "title": title,
                    "url": final_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })

                if len(offers) >= max_items * 2:
                    logging.info(f"Trovate {len(offers)} offerte su {url}")
                    return offers[:max_items*3]

        except Exception as e:
            logging.error(f"Errore su {url}: {e}")

    return offers
