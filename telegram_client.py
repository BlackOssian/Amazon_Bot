# telegram_client.py – VERSIONE 2025 CHE FUNZIONA DAVVERO CON @username
import os
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@superamaz0n")  # funziona con @username se bot è admin

bot = Bot(token=TELEGRAM_TOKEN)

async def _send_photo(offer):
    caption = (
        f"<b>{offer['title']}</b>\n"
        f"💰 <b>Prezzo:</b> {offer['price']} {offer['currency']}\n"
        f"🔗 <a href=\"{offer['url']}\">Vai all'offerta su Amazon</a>"
    )
    
    await bot.send_photo(
        chat_id=TELEGRAM_CHAT_ID,
        photo=offer["image"],
        caption=caption,
        parse_mode=ParseMode.HTML,
        read_timeout=20,
        write_timeout=20,
        connect_timeout=20,
        pool_timeout=20
    )

def send_offer_photo(offer):
    try:
        asyncio.run(_send_photo(offer))
        logging.info(f"POSTATA SU {TELEGRAM_CHAT_ID}: {offer['title'][:60]}...")
    except Exception as e:
        logging.error(f"ERRORE TELEGRAM (finalmente visibile): {e}")
