import pytest
from apps.notifications.models import Notification, statusChoices
from apps.notifications.tasks import send_notification_task
from rest_framework import status
from unittest.mock import Mock


@pytest.mark.django_db
def test_invalid_chat_id(monkeypatch):
  """
  Пользователь указал неверный chat_id
  """
  mock_response = Mock()
  mock_response.status_code = status.HTTP_400_BAD_REQUEST
  monkeypatch.setattr('apps.notifications.telegram.requests.post', lambda *args, **kwargs: mock_response)

  notification = Notification.objects.create(
      channel='TELEGRAM',
      recipient='999999999',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )


  with pytest.raises(ValueError):
    send_notification_task(notification.id)
  notification.refresh_from_db()

  assert notification.status == statusChoices.FAILED



@pytest.mark.django_db
def test_retry_after_500(monkeypatch):
  """
    Проверяем, что retry работает после ошибки 500 от телеграма
  """
  mock_response = Mock()
  mock_response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
  monkeypatch.setattr('apps.notifications.telegram.requests.post', lambda *args, **kwargs: mock_response)

  notification = Notification.objects.create(
      channel='TELEGRAM',
      recipient='1393300917',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )


  with pytest.raises(ConnectionError):
    send_notification_task(notification.id)
  notification.refresh_from_db()

  assert notification.status == statusChoices.PROCESSING
