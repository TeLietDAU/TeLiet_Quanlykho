import uuid
from django.db import models

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'categories'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    base_price = models.DecimalField(max_digits=19, decimal_places=4, default=0)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    base_unit = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')

    class Meta:
        db_table = 'products'

class ProductUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='units')
    unit_name = models.CharField(max_length=100)
    conversion_rate = models.DecimalField(max_digits=19, decimal_places=4, default=1.0)

    class Meta:
        db_table = 'product_units'