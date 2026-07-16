import requests
from django.conf import settings


def send_telegram_notification(text):
    URL = (
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_KEY}/sendMessage"
    )

    response = requests.post(
        URL,
        json={"chat_id": settings.TELEGRAM_CHAT_ID, "text": text},
        timeout=5,
    )
    return response
