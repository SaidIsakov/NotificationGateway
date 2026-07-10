from smtplib import SMTPServerDisconnected
from celery import shared_task
from django.db import transaction
from django.forms import ValidationError
from apps.notifications.models import Notification, statusChoices, channelChoices
import logging
from django.core.mail import send_mail
from django.conf import settings
from apps.notifications.telegram import send_notification_from_tg


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=2)
def send_notification_task(self, notification_id):
  notification = None
  try:
    with transaction.atomic():
      notification = Notification.objects.get(id=notification_id)
      notification.status = statusChoices.PROCESSING
      notification.save()
    logger.info(f"Sending notification {notification_id}")
    if notification.channel == channelChoices.EMAIL:
      send_mail(
          subject=notification.payload.get('subject', 'No subject'),
          message=notification.payload.get('text', ''),
          from_email=settings.EMAIL_HOST_USER,
          recipient_list=[notification.recipient],
          fail_silently=False,
      )
    else:
      send_notification_from_tg(notification)
    with transaction.atomic():
      notification.status = statusChoices.SENT
      notification.save()
  except Notification.DoesNotExist:
    logger.error(f"Notification {notification_id} does not exist")
    raise
  except (ConnectionError, TimeoutError, SMTPServerDisconnected) as e:
    current_attempt = self.request.retries + 1
    max_attempts = self.max_retries
    new_line = f"Attempt {current_attempt}/{max_attempts} failed: {str(e)}"

    if notification:
      current_error_message = notification.error_message
      if notification.error_message is not None:
        if current_error_message:
          notification.error_message = notification.error_message + "\n" + new_line
      else:
        notification.error_message = new_line
      notification.save()
      logger.warning(str(e))
      self.retry(exc=e, countdown = 2 ** self.request.retries)
  except ValidationError as e:
    # Non-retry-able ошибка
    if notification:
      notification.status = statusChoices.FAILED
      notification.error_message = f"Fatal error: {str(e)}"
      logger.error(f"Fatal error, id_notification: {notification.id}, error: {str(e)}")
      notification.save()
      raise
  except Exception as e:
    if notification:
      notification.status = statusChoices.FAILED
      notification.error_message = str(e)
      notification.save()
      raise
