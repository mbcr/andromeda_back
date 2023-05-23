from django.contrib import admin

# Register your models here.
from .models import FeatureAccessCode, Authorisation

admin.site.register(FeatureAccessCode)
admin.site.register(Authorisation)