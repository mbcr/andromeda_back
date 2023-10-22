from django.contrib import admin

# Register your models here.
from .models import RequestEvent, AccessLog

admin.site.register(RequestEvent)
admin.site.register(AccessLog)