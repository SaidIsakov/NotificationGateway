from rest_framework import serializers
from .models import Product

class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Product
    fields = ['id', 'name', 'stock']
    read_only_fields = ['id']


