from django.urls import path

from .views import AssessmentView, CreateAPIKeyView, DeleteAPIKeyView

urlpatterns = [
    path('assessment/', AssessmentView.as_view()),
    path('create_api_key/<str:api_key_name>/', CreateAPIKeyView.as_view()),
    path('delete_api_key/<str:api_key_prefix>/', DeleteAPIKeyView.as_view()),

]
