from rest_framework import generics
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer


class CreateNotification(generics.CreateAPIView):
  queryset = Notification.objects.all()
  serializer_class = NotificationSerializer


class RetrieveNotification(generics.RetrieveAPIView):
  queryset = Notification.objects.all()
  serializer_class = NotificationSerializer
  lookup_field = 'id'
