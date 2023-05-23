from django.contrib import admin

# Register your models here.
from .models import RequestEvent, LandingPagePipelineLog

admin.site.register(RequestEvent)
admin.site.register(LandingPagePipelineLog)