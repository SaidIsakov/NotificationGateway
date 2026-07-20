from django.contrib import admin
from apps.analytics.models import OrderEvent, DailyMetrics

@admin.register(OrderEvent)
class OrderEventAdmin(admin.ModelAdmin):
  pass


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
  pass
