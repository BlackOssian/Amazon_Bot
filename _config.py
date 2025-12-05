# config.py
# config.py

# 1. Credenziali di Affiliazione Amazon
# Sostituisci con il tuo Tracking ID (es. "offerte123-21")
AMAZON_TRACKING_ID = "darkitalia-21" 

# 2. Credenziali del Bot Telegram
# Token del Bot ottenuto da @BotFather
TELEGRAM_BOT_TOKEN = "8281603203:AAEkKvUNgJs_khi7KDXfc1xGEjtCKalP2ts" 
# Nome utente del tuo canale pubblico (es. "@offertedelgiorno")
TELEGRAM_CHANNEL_USERNAME = "@superamaz0n" 

# 3. URL di Test Amazon (Deve puntare a un prodotto esistente su Amazon.it)
# Per esempio, usa il link che ha funzionato prima:
TEST_AMAZON_URL = "https://www.amazon.it/deals"

# 4. File per evitare la pubblicazione di duplicati
PUBLISHED_ASIN_FILE = "published_asin.txt"