from django.contrib import admin
from .models import Assessment, PreOrder, Order

# Register your models here.
admin.site.register(Assessment)
admin.site.register(Order)
admin.site.register(PreOrder)