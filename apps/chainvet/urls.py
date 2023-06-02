from django.urls import path

from .views import AssessmentCreateWIthAPIKeyView, AssessmentCreateWIthUserView, AssessmentListView, AssessmentDetailView
from .views import CreateAPIKeyView, DeleteAPIKeyView

urlpatterns = [
    path('assessment/', AssessmentCreateWIthAPIKeyView.as_view(), name='assessment-create-with-api-key'),
    path('assessments/create/', AssessmentCreateWIthUserView.as_view(), name='assessment-create-with-user'),
    path('assessments/list/', AssessmentListView.as_view(), name='assessment-list'),
    path('assessments/<str:assessment_id>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('create_api_key/<str:api_key_name>/', CreateAPIKeyView.as_view()),
    path('delete_api_key/<str:api_key_prefix>/', DeleteAPIKeyView.as_view()),

]
