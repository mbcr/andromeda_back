from rest_framework import serializers
from .models import Assessment, Order
from apps.users import models as user_models

from rest_framework import serializers
from datetime import datetime

class AccessCodeFullSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    assessments = serializers.SerializerMethodField()
    list_of_api_keys_references = serializers.SerializerMethodField()

    def get_access_code_orders(self, obj):
        return OrderSerializer(obj.orders, many=True).data
    def get_access_code_assessments(self, obj):
        return list(obj.assessments.values_list('assessment_id', flat=True))
    def get_list_of_api_keys_references(self, obj):
        return list(obj.api_keys.values_list('reference', flat=True))
    
    class Meta:
        model = user_models.AccessCode
        fields = [
            'code',
            'start_date',
            'email',
            'affiliate_origin',
            'credits_paid_for',
            'credits_used',
            'credits_available',
            'orders',
            'assessments',
            'list_of_api_keys_references',
        ]

    def to_representation(self, instance):
        # Update credit cache before serialization
        instance.set_credit_cache()
        return super(AccessCodeFullSerializer, self).to_representation(instance)

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

class CustomUserFullSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()
    assessments = serializers.SerializerMethodField()
    list_of_api_keys_references = serializers.SerializerMethodField()

    def get_access_code_orders(self, obj):
        return OrderSerializer(obj.orders, many=True).data
    def get_access_code_assessments(self, obj):
        return list(obj.assessments.values_list('assessment_id', flat=True))
    def get_list_of_api_keys_references(self, obj):
        return list(obj.api_keys.values_list('reference', flat=True))
    
    class Meta:
        model = user_models.CustomUser
        fields = [
            'start_date',
            'email',
            'affiliate_origin',
            'credits_paid_for',
            'credits_used',
            'credits_available',
            'orders',
            'assessments',
            'list_of_api_keys_references',
        ]

    def to_representation(self, instance):
        # Update credit cache before serialization
        instance.set_credit_cache()
        return super(CustomUserFullSerializer, self).to_representation(instance)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'order_id',
            'created_at',
            'affiliate',
            'number_of_credits',
            'total_price_usd_cents',
            'payment_coin',
            'payment_network',
            'total_price_crypto',
            'payment_address',
            'payment_memo',
            'swap_details',
            'status',
            'is_paid',
            'paid_at',
        ]