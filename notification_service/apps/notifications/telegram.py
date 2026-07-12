from django.conf import settings
import requests


def send_notification_from_tg(notification):
  response = requests.post(
        settings.TELEGRAM_API_URL,
        json={
            'chat_id': notification.recipient,
            'text': f"{notification.payload.get('subject', '')}\n\n{notification.payload.get('text', '')}"
        },
        timeout=10
    )
  if response.status_code == 400:
    raise ValueError("Invalid chat_id")
  elif response.status_code >= 500:
    raise ConnectionError("Telegram error")

  return response
