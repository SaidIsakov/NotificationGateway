from decimal import Decimal
from django.db import models


class OrderEvent(models.Model):
  EVENT_TYPES = [
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
  ]

  event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
  order_id = models.UUIDField()
  product_name = models.CharField(max_length=255)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  created_at = models.DateTimeField(auto_now_add=True)


class DailyMetrics(models.Model):
  date = models.DateField(unique=True)
  total_orders = models.IntegerField(default=0)
  paid_orders = models.IntegerField(default=0)
  cancelled_orders = models.IntegerField(default=0)
  total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
  conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
