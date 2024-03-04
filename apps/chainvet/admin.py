from django.contrib import admin
from .models import Assessment, AssessmentAdmin, Order, OrderAdmin

# Register your models here.
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(PreOrder)