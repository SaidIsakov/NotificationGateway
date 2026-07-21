from apps.analytics.models import DailyMetrics, OrderEvent
from apps.analytics.serializers import DailyMetricsSerializer
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from apps.analytics.pagination import DailyMetricsPagination
from django.utils import timezone
from datetime import timedelta
from rest_framework.response import Response
from django.db.models import Count, Sum


class DailyMetricsListAPIView(ListAPIView):
  serializer_class = DailyMetricsSerializer
  pagination_class = DailyMetricsPagination
  queryset = DailyMetrics.objects.all().order_by('-date')


class DailyMetricsAPIView(APIView):

  def get(self, request, *args, **kwargs):
    """
      Статистика за последние 7 дней
    """
    seven_days_ago = timezone.now().date() - timedelta(days=7)
    result = DailyMetrics.objects.filter(date__gte=seven_days_ago).aggregate(
      total_orders = Count('id'),
      total_revenue = Sum('total_revenue'),
      avg_conversion_rate = Sum('conversion_rate') / Count('conversion_rate')
    )
    data = {
      "period": "last_7_days",
      "total_orders": result['total_orders'],
      "total_revenue": result['total_revenue'],
      "avg_conversion_rate": result['avg_conversion_rate']
    }
    return Response(data, status=200)


class OrderEventAPIView(APIView):

  def get(self, request, *args, **kwargs):
    """
    Топ 5 самых заказываемых товаров за последние 30 дней
    """
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    products = OrderEvent.objects.filter(
      created_at__gte=thirty_days_ago,
      event_type='paid'
    ).values('product_name').annotate(
      orders_count=Count('id')
      ).order_by('-orders_count')[:5]



    data = {
      'products': list(products)
    }
    return Response(data)
