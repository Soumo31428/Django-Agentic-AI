from django.contrib import admin
from .models import Product, Order, RefundRequest
# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(RefundRequest)