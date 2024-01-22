from django.urls import path

from .views import *


urlpatterns = [
    path('assessment/', AssessmentCreateWIthAPIKeyView.as_view(), name='assessment-create-with-api-key'),
    path('assessments/create/', AssessmentCreateWIthUserView.as_view(), name='assessment-create-with-user'),
    path('assessments/list/', AssessmentListView.as_view(), name='assessment-list'),
    # path('assessments/<str:assessment_id>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('create_api_key/<str:api_key_name>/', CreateAPIKeyView.as_view()),
    path('delete_api_key/<str:api_key_prefix>/', DeleteAPIKeyView.as_view()),
    path('accesscode/status/', check_access_code_status, name='access-code-check-status'),
    path('accesscode/create/assessment/', create_new_assessment_for_access_code, name='assessment-create-with-access-code'),
    path('accesscode/assessments/', check_assessment_list_for_access_code, name='access-code-check-status'),
    path('order/create/', create_new_order, name='order-create-create'),
    path('order/status/', check_order_status, name='order-check-status'),
    path('user/status/', check_self_status, name='user-check-status'),
    path('user/create/assessment/', create_new_assessment_for_user, name='assessment-create-with-user'),
]
