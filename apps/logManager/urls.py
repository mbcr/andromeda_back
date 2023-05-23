from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import log_landing_page_usage

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls))
]

urlpatterns.append(path('datastream/', log_landing_page_usage, name='log_landing_page_usage'))
