from django.contrib import admin
from .models import Assessment, AssessmentAdmin, PreOrder, Order

# Register your models here.
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Order)
admin.site.register(PreOrder)