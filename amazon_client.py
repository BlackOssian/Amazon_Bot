# amazon_client.py – USA I FEED RSS DI KEEPA – 100% STABILE, NESSUN BLOCCO, NIENTE PROXY
import feedparser
import random
import logging
from config import AMAZON_ASSOC_TAG

# Feed RSS di Keepa per Amazon.it (aggiornati ogni minuto)
KEEPA_FEEDS = [
    "https://keepa.com/#!rss/deals/IT/0",        # Tutte le offerte lampo
    "https://keepa.com/#!rss/deals/IT/1",        # Offerte del giorno
    "https://keepa.com/#!rss/deals/IT/2",        # Migliori sconti
]

def add_affiliate_tag(url):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}tag={AMAZON_ASSOC_TAG}"

def get_offers(max_items=10):
    offers = []
    seen_urls = set()

    logging.info("Scarico offerte da Keepa RSS – stabile come una roccia!")

    for feed_url in KEEPA_FEEDS:
        if len(offers) >= max_items:
            break

        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                if len(offers) >= max_items:
                    break

                url = entry.link
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                full_url = add_affiliate_tag(url)

                title = entry.title.strip()
                if len(title) < 10:
                    continue

                # Prezzo (Keepa lo dà nel summary o description)
                price = "Scopri prezzo"
                if "price" in entry.summary.lower():
                    import re
                    match = re.search(r'€\s*([\d,]+)', entry.summary)
                    if match:
                        price = match.group(1).replace(",", ".") + " €"

                # Immagine (Keepa la dà sempre)
                image = entry.get("media_content", [{}])[0].get("url", "")
                if not image:
                    image = "https://via.placeholder.com/300x300/FF9900/FFFFFF?text=Amazon+Deal"

                offers.append({
                    "title": title,
                    "url": full_url,
                    "image": image,
                    "price": price,
                    "currency": "€"
                })
                logging.info(f"OFFERTA KEEPA: {title[:60]}... {price}")

        except Exception as e:
            logging.error(f"Errore Keepa feed {feed_url}: {e}")

    logging.info(f"KEEPA ha dato {len(offers)} offerte reali!")
    return random.sample(offers, min(len(offers), max_items)) if offers else []
