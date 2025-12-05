from telegram import Bot
from telegram.constants import ParseMode # Modifica qui
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)

def send_offer_photo(offer):
    """
    offer: dict con chiavi title, url, image, price, currency
    """
    title = offer["title"]
    url = offer["url"]
    image = offer["image"]
    price = offer["price"]
    currency = offer.get("currency", "€")

    caption = (
        f"<b>{title}</b>\n"
        f"💰 <b>Prezzo:</b> {price} {currency}\n"
        f"🔗 <a href=\"{url}\">Vai all'offerta su Amazon</a>"
    )

    bot.send_photo(
        chat_id=TELEGRAM_CHAT_ID,
        photo=image,
        caption=caption,
        parse_mode=ParseMode.HTML, # Ora ParseMode.HTML è l'oggetto corretto
    )