from celery import shared_task
from django.db import transaction
from apps.notifications.models import Notification, statusChoices
import time
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_notification_task(notification_id):
  try:
    with transaction.atomic():
      notification = Notification.objects.get(id=notification_id)
      notification.status = statusChoices.PROCESSING
    logger.info(f"Sending notification {notification_id}")
    time.sleep(3)
    with transaction.atomic():
      notification.status = statusChoices.SENT
  except Exception as e:
    notification.status = statusChoices.FAILED
    notification.error_message = str(e)
  finally:
    notification.save()
