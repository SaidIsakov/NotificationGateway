from celery.exceptions import Retry
import pytest
from apps.notifications.tasks import send_notification_task
from apps.notifications.models import Notification, statusChoices
from rest_framework.exceptions import ValidationError


@pytest.mark.django_db
def test_notification_is_sent(monkeypatch):
  """
    Уведомление отправлено успешно
  """

  monkeypatch.setattr('apps.notifications.tasks.send_mail', lambda **kwargs: None)

  notification = Notification.objects.create(
      channel='EMAIL',
      recipient='test@gmail.com',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )

  send_notification_task(notification.id)

  notification.refresh_from_db()

  assert notification.status == statusChoices.SENT


def mock_send_mail_connection_error(**kwargs):
    raise ConnectionError("Simulated Connection error")

@pytest.mark.django_db
def test_connectionError_retry(monkeypatch):
  """
    Проверяем retry
  """
  monkeypatch.setattr('apps.notifications.tasks.send_mail', mock_send_mail_connection_error)

  notification = Notification.objects.create(
      channel='EMAIL',
      recipient='test@gmail.com',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )

  with pytest.raises(Exception):
    send_notification_task(notification.id)
  notification.refresh_from_db()
  assert notification.status == 'PROCESSING'
  assert 'Attempt 1/3 failed' in notification.error_message # pyright: ignore[reportOperatorIssue]


def mock_send_mail_validation_error(**kwargs):
    raise ValidationError("Simulated Validation error")

@pytest.mark.django_db
def test_retry_not_aply(monkeypatch):
  """
    retry не срабатывает после ValidationError
  """
  monkeypatch.setattr('apps.notifications.tasks.send_mail', mock_send_mail_validation_error)

  notification = Notification.objects.create(
      channel='EMAIL',
      recipient='test@gmail.com',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )

  with pytest.raises(Exception):
    send_notification_task(notification.id)
  notification.refresh_from_db()
  assert notification.status == 'FAILED'
  assert len(notification.error_message) > 0

