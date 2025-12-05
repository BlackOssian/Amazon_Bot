from telegram import Bot
from telegram.constants import ParseMode
import os
import logging

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@superamaz0n")

bot = Bot(token=TOKEN)

def send_offer_photo(offer):
    caption = (
        f"<b>{offer['title']}</b>\n"
        f"💰 <b>Prezzo:</b> {offer['price']} {offer['currency']}\n"
        f"🔗 <a href=\"{offer['url']}\">Vai all'offerta su Amazon</a>"
    )

    try:
        bot.send_photo(
            chat_id=CHAT_ID,
            photo=offer["image"],
            caption=caption,
            parse_mode=ParseMode.HTML
        )
        logging.info(f"POSTATA SU {CHAT_ID}: {offer['title'][:50]}...")
    except Exception as e:
        logging.error(f"ERRORE TELEGRAM: {e}")
