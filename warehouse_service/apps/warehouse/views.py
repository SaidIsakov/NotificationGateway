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
      if product.stock > 0:
        product.stock -= 1
        product.save()
        logger.info(f"The {product.name} written off")
        return Response({"status": f"The {product.name} written off"}, status=200)
      elif product.stock == 0:
        logger.warning(f"Товар {product.name} закончился на складе!")
        return Response({"status": "out_of_stock", "message": "Товара нет в наличии"}),

    except Product.DoesNotExist:
      logger.warning(f"Товар с названием/slug '{product_name}' не найден на складе")
      return Response({"status": "Product does not exist"}, status=404)
