from rest_framework import generics
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.tasks import send_notification_task


class CreateNotification(generics.CreateAPIView):
  queryset = Notification.objects.all()
  serializer_class = NotificationSerializer

  def perform_create(self, serializer):
    notification = serializer.save()

    if notification:
      send_notification_task.delay(notification.id)


class RetrieveNotification(generics.RetrieveAPIView):
  queryset = Notification.objects.all()
  serializer_class = NotificationSerializer
  lookup_field = 'id'
