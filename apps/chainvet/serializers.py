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
    assessment_updated_at = serializers.DateTimeField(format="%d/%m/%Y-%Hh%M")
    risk_score = serializers.SerializerMethodField()

    def get_risk_score(self, obj):
        return f"{obj.risk_score * 100:.1f}%"

    class Meta:
        model = Assessment
        fields = [
            'assessment_id',
            'time_of_request',
            'type_of_assessment',
            'address_hash',
            'address_hash_short',            
            'transaction_hash',
            'transaction_hash_short',
            'currency',
            'status_assessment',
            'risk_score',
            'risk_grade',
            'risk_signals',
            'risk_volume_coin',
            'risk_volume_fiat',
            'assessment_updated_at',
            'transaction_volume_coin',
            'transaction_volume_fiat',
            'transaction_volume_fiat_currency_code',
            
        ]