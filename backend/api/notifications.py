import os

import requests
from django.conf import settings

from .order_flow import get_status_label


def _telegram_api_url(method: str) -> str:
    token = getattr(settings, "BOT_TOKEN", "") or os.getenv("BOT_TOKEN", "")
    return f"https://api.telegram.org/bot{token}/{method}"


def send_order_status_notification(order) -> bool:
    user = getattr(order, "user", None)
    if not user or not getattr(user, "notification_order_status", True):
        return False

    if not getattr(user, "tg_id", None):
        return False

    status_label = get_status_label(getattr(order, "status", None))
    track_code = order.track_code or str(order.id)
    text = f"Заказ #{track_code}\nСтатус: {status_label}"

    payload = {
        "chat_id": user.tg_id,
        "text": text,
    }
    try:
        response = requests.post(_telegram_api_url("sendMessage"), json=payload, timeout=10)
        data = response.json()
        return response.status_code == 200 and data.get("ok")
    except Exception:
        return False
