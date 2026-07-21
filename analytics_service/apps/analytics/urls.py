from django.urls import path
from apps.analytics.views import DailyMetricsListAPIView, DailyMetricsAPIView, OrderEventAPIView

urlpatterns = [
  path('daily/', DailyMetricsListAPIView.as_view(), name='analytics-daily'),
  path('summary/', DailyMetricsAPIView.as_view(), name='analytics-summary'),
  path('top-products/', OrderEventAPIView.as_view(), name='analytics-top-products')
]

