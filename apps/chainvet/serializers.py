from rest_framework import serializers
from .models import Assessment

from rest_framework import serializers
from datetime import datetime

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'

class AssessmentListSerializer(serializers.ModelSerializer):
    time_of_request = serializers.DateTimeField(format="%d/%m/%Y-%Hh%M")
    class Meta:
        model = Assessment
        fields = [
            'assessment_id',
            'time_of_request',
            'type_of_assessment',
            'address_hash',
            'transaction_hash',
            'currency',
            'status_assessment',
            'risk_score',
            'risk_grade'
        ]