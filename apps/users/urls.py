from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserDetails, UserTier

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls))
]

urlpatterns.append(path('userdetails/', UserDetails, name='user-details'))
urlpatterns.append(path('user/tier/', UserTier, name='user-tier'))