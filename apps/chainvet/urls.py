from django.urls import path

from .views import AssessmentView

urlpatterns = [
    path('assessment/', AssessmentView.as_view()),
]
