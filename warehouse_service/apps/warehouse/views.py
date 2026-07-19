from os import name
from django.shortcuts import render
from rest_framework.views import APIView
from apps.warehouse.models import Product
import logging
from rest_framework.response import Response
from django.utils.text import slugify


logger = logging.getLogger(__name__)

class WarehouseAPIView(APIView):

  def get(self, request, product_name: str):
    product_slug = slugify(product_name)
    try:
      product = Product.objects.get(slug=slugify(product_slug))
      return Response({"name": product.name, "stock": product.stock}, status=200)
    except Product.DoesNotExist:
      return Response({"status": "Product does not exist"}, status=404)
