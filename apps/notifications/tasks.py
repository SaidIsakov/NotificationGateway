from celery import shared_task
from django.db import transaction
from apps.notifications.models import Notification, statusChoices
import time
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_notification_task(notification_id):
  try:
    with transaction.atomic():
      notification = Notification.objects.get(id=notification_id)
      notification.status = statusChoices.PROCESSING
    logger.info(f"Sending notification {notification_id}")
    send_mail(
          subject=notification.payload.get('subject', 'No subject'),
          message=notification.payload.get('text', ''),
          from_email=settings.EMAIL_HOST_USER,
          recipient_list=[notification.recipient],
          fail_silently=False,
    )
    with transaction.atomic():
      notification.status = statusChoices.SENT
  except Exception as e:
    notification.status = statusChoices.FAILED
    notification.error_message = str(e)
  finally:
    notification.save()
