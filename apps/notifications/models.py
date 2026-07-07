from django.db import models
import uuid

class channelChoices(models.TextChoices):
  EMAIL = 'EMAIL', 'Email'
  TELEGRAM = 'TELEGRAM', 'Telegram'
  PUSH = 'PUSH', 'Push'


class statusChoices(models.TextChoices):
   PENDING = 'PENDING', 'Pending'
   PROCESSING = 'PROCESSING', 'Processing'
   SENT = 'SENT', 'Sent'
   FAILED = 'FAILED', 'Failed'


class Notification(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  channel = models.CharField(choices=channelChoices.choices, max_length=20)
  recipient = models.CharField(max_length=255)
  payload = models.JSONField()
  status = models.CharField(choices=statusChoices.choices, max_length=15, default='PENDING')
  error_message = models.TextField(blank=True, null=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
