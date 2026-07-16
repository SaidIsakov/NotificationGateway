from django.urls import path
from apps.warehouse.views import WarehouseAPIView


urlpatterns = [
    path('warehouse/<slug:product_name>/', WarehouseAPIView.as_view(), name='warehouse')
]

