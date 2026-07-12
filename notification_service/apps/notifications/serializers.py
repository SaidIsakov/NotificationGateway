from rest_framework import serializers
from apps.notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):

  class Meta:
    model = Notification
    fields = ['id', 'status', 'error_message',
        'payload', 'channel', 'recipient',
        'created_at', 'updated_at'
    ]
    read_only_fields = ['id', 'status', 'error_message']

  def validate_payload(self, value):
    """
      Проверяем, что payload - словарь
    """
    if not isinstance(value, dict):
      raise serializers.ValidationError('payload must be dict')
    return value


