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

  return response
