# telegram_client.py – FUNZIONA CON @username DEL CANALE (NO ID NUMERICO)
from telegram import Bot
from telegram.constants import ParseMode
import os
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@superamaz0n")  # Usa @username

bot = Bot(token=TELEGRAM_TOKEN)

async def send_offer_photo_async(offer):
    caption = (
        f"<b>{offer['title']}</b>\n"
        f"💰 <b>Prezzo:</b> {offer['price']} {offer['currency']}\n"
        f"🔗 <a href=\"{offer['url']}\">Vai all'offerta su Amazon</a>"
    )
    await bot.send_photo(
        chat_id=TELEGRAM_CHAT_ID,
        photo=offer["image"],
        caption=caption,
        parse_mode=ParseMode.HTML
    )

def send_offer_photo(offer):
    import asyncio
    try:
        asyncio.run(send_offer_photo_async(offer))
        logging.info(f"POSTATA SU @{TELEGRAM_CHAT_ID.split('@')[1]}: {offer['title'][:50]}...")
    except Exception as e:
        logging.error(f"Errore Telegram: {e}")
