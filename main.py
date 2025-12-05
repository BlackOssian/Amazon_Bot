# main.py – VERSIONE FINALE FREE 24/7 per Render (dicembre 2025)

import os
import time
import logging
import threading
from flask import Flask
from amazon_client import get_offers
from telegram_client import send_offer_photo

# ===================== FLASK PER TENERE VIVO IL FREE TIER =====================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Amazon Affiliato FREE 24/7 - Pompa offerte mentre tu dormi! 💸🔥"

def run_flask():
    port = int(os.environ.get("PORT", 10000))   # Render decide la porta, noi obbediamo
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ===================== LOGGING BELLO E SALVATO SU FILE =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("amazon_bot.log"),
        logging.StreamHandler()
    ]
)

# ===================== CONFIGURAZIONE CICLO =====================
CHECK_INTERVAL = 4 * 60 * 60   # 4 ore tra un giro e l'altro
MAX_OFFERS_PER_RUN = 8

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
    offers = get_offers(max_items=MAX_OFFERS_PER_RUN * 2)   # ne prendo di più per sicurezza

    if not offers:
        logging.error("Nessuna offerta trovata, riprovo al prossimo giro.")
        return

    nuove = 0
    for offer in offers:
        if offer["url"] in posted_urls:
            continue

        try:
            send_offer_photo(offer)
            posted_urls.add(offer["url"])
            save_posted_url(offer["url"])
            nuove += 1
            logging.info(f"Postata: {offer['title'][:60]}...")
            time.sleep(3)   # anti-flood Telegram
        except Exception as e:
            logging.error(f"Errore invio Telegram: {e}")

    logging.info(f"Giro finito – {nuove} nuove offerte pubblicate nel canale!")

# ===================== AVVIO =====================
if __name__ == "__main__":
    # 1. Avvia Flask in background (tiene viva la porta → Render FREE non dorme più)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    port = os.environ.get("PORT", 10000)
    logging.info(f"FLASK AVVIATO sulla porta {port} – FREE TIER 24/7 ATTIVO! NIENTE SOLDI DEL CAZZO!")

    # 2. Avvio vero del bot
    logging.info("Bot Amazon affiliato avviato – modalità 24/7")
    posted_urls = load_posted_urls()

    # Primo giro subito
    run_once()

    # Ciclo infinito
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            run_once()
        except KeyboardInterrupt:
            logging.info("Bot fermato manualmente. Ciao fratello!")
            break
        except Exception as e:
            logging.error(f"Errore grave ma continuo a vivere: {e}")
            time.sleep(60)
