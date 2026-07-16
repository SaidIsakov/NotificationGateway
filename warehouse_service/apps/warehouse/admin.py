from django.contrib import admin
from apps.warehouse.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
  prepopulated_fields = {'slug': ('name',)}
