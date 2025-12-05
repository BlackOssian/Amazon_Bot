# main.py
import time
import logging
from datetime import datetime
from amazon_client import get_offers
from telegram_client import send_offer_photo

# Logging carino così vedi che cazzo succede
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("amazon_bot.log"),
        logging.StreamHandler()
    ]
)

# Quante ore tra un giro e l'altro (es. ogni 4 ore = 14400 secondi)
CHECK_INTERVAL = 4 * 60 * 60  # 4 ore
MAX_OFFERS_PER_RUN = 5

# Per non ripostare le stesse offerte all'infinito
posted_urls = set()

def load_posted_urls():
    try:
        with open("posted.txt", "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_posted_url(url):
    with open("posted.txt", "a", encoding="utf-8") as f:
        f.write(url + "\n")

def run_once():
    logging.info("Inizio scraping Amazon...")
    offers = get_offers(keywords="offerte lampo", max_items=20)  # ne prendo di più e poi filtro
    
    if not offers:
        logging.error("Nessuna offerta trovata, riprovo al prossimo giro.")
        return

    new_offers = 0
    for offer in offers:
        if offer["url"] in posted_urls:
            continue  # già postata, salta
            
        try:
            send_offer_photo(offer)
            posted_urls.add(offer["url"])
            save_posted_url(offer["url"])
            new_offers += 1
            logging.info(f"Postata: {offer['title'][:60]}...")
            time.sleep(3)  # anti-flood Telegram
        except Exception as e:
            logging.error(f"Errore invio Telegram: {e}")
    
    logging.info(f"Giro completato - {new_offers} nuove offerte postate.")

if __name__ == "__main__":
    logging.info("Bot Amazon affiliato avviato - modalità 24/7")
    posted_urls = load_posted_urls()
    
    # Primo giro subito
    run_once()
    
    # Poi cicla all'infinito
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            run_once()
        except KeyboardInterrupt:
            logging.info("Bot fermato manualmente. Ciao bello!")
            break
       