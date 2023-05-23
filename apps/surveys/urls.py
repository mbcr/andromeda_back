from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls))
]

urlpatterns.append(path('surveys/checkrespondent/', check_respondent, name='check_respondent'))
urlpatterns.append(path('surveys/getquestions/', get_survey_questions, name='get_survey_questions'))
urlpatterns.append(path('surveys/submitanswers/', save_answers, name='submit_answers'))







