import pytest
from rest_framework import status
from apps import notifications
from apps.notifications.models import Notification, statusChoices


@pytest.mark.django_db
def test_post_notification(create_user, create_api_client):
  """
   Корректно создает уведомление и возвращает 201
  """
  misha = create_user('Misha')
  client = create_api_client(misha)
  url = '/api/v1/notifications/'
  data = {
    "payload": {
      "text": "Test Hello"
    },
    "channel": "EMAIL",
    "recipient": "test@gmail.com"
  }
  response = client.post(url, data, format="json")

  assert response.status_code == status.HTTP_201_CREATED
  assert response.data["payload"]["text"] == 'Test Hello'
  assert response.data["status"] == "PENDING"
  assert Notification.objects.count() == 1


@pytest.mark.django_db
def test_post_invalid_channel_notification(create_user, create_api_client):
  """
    Создаем уведобление с некорректным channel
  """
  misha = create_user('Misha')
  client = create_api_client(misha)
  url = '/api/v1/notifications/'
  data = {
    "payload": {
      "text": "Test Hello"
    },
    "channel": "Invalid",
    "recipient": "test@gmail.com"
  }
  response = client.post(url, data, format="json")
  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_post_invalid_payload_notification(create_user, create_api_client):
  """
    Создаем уведобление с некорректным payload
  """
  misha = create_user('Misha')
  client = create_api_client(misha)
  url = '/api/v1/notifications/'
  data = {
    "payload": [1, 2, 3],
    "channel": "Invalid",
    "recipient": "test@gmail.com"
  }
  response = client.post(url, data, format="json")
  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert Notification.objects.count() == 0


@pytest.mark.django_db
def test_get_notification(create_user, create_api_client):
  """
    Возвращает уведомление с правильным статусом
  """
  misha = create_user('Misha')
  client = create_api_client(misha)

  notification = Notification.objects.create(
      channel='EMAIL',
      recipient='test@gmail.com',
      payload={'subject': 'Test', 'text': 'Hello'},
      status=statusChoices.PENDING
  )

  url = f'/api/v1/notifications/{notification.id}/'

  response = client.get(url)

  assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_non_existent_notification(create_user, create_api_client):
  """
    Получение несуществующего уведомления
  """
  misha = create_user('Misha')
  client = create_api_client(misha)



  url = f'/api/v1/notifications/ad39a170-46e4-4c0e-b78d-c2f5fec7edvv/'

  response = client.get(url)

  assert response.status_code == status.HTTP_404_NOT_FOUND
