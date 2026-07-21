from apps.analytics.models import DailyMetrics
from rest_framework import serializers


class DailyMetricsSerializer(serializers.ModelSerializer):
  class Meta:
    model = DailyMetrics
    fields = ['date', 'total_orders', 'paid_orders',
              'cancelled_orders', 'total_revenue', 'conversion_rate']
