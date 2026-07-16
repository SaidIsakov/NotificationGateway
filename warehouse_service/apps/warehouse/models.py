from django.db import models
from django.utils.text import slugify


class Product(models.Model):
  name = models.CharField(max_length=255, unique=True)
  stock = models.PositiveIntegerField(default=0)
  slug = models.SlugField(max_length=100, blank=True, null=True)

  def save(self, *args, **kwargs):
    if not self.pk:
      self.slug = slugify(self.name)
    super().save(*args, **kwargs)

  def __str__(self):
      return self.name
  
