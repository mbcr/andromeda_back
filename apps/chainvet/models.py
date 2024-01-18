from django.db import models
from django.db.models import JSONField
from django.contrib import admin
from django.contrib.auth import get_user_model



class Order(models.Model):
    class OwnerType(models.TextChoices):
        USER = 'User', 'User'
        ACCESSCODE = 'AccessCode', 'AccessCode'

    owner_type = models.CharField(
        max_length=10,
        choices=OwnerType.choices,
        default=OwnerType.USER,
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'pre_orders'
    )
    access_code = models.ForeignKey(
        'users.AccessCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'pre_orders'
    )
    order_id = models.CharField(max_length=12, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    affiliate = models.ForeignKey(to='users.Affiliate', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    last_interaction = models.DateTimeField(auto_now=True, null=True, blank=True)
    number_of_credits = models.IntegerField(default=0)
    total_price_usd_cents = models.FloatField(default=0)
    payment_coin = models.CharField(max_length=10, null=True, blank=True)
    payment_network = models.CharField(max_length=10, null=True, blank=True)
    total_price_crypto = models.FloatField(default=0)
    payment_is_direct = models.BooleanField(default=False)
    payment_address = models.CharField(max_length=128, null=True, blank=True)
    payment_memo = models.CharField(max_length=128, null=True, blank=True)
    swap_details = JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, null=True, blank=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        paid_date = self.paid_at.strftime('%Y.%m.%d %Hh%Mm%Ss') if self.paid_at else ''
        return f'Order {self.id} - {self.created_at.strftime("%Y.%m.%d %Hh%Mm%Ss")} - {self.number_of_credits} credits - By: {self.owner_type} - PAID: {self.is_paid} {paid_date}.'

class AssessmentAdmin(admin.ModelAdmin):
    list_filter = ['user', 'access_code', 'type_of_assessment']
class Assessment(models.Model):
    TYPE_CHOICES = [
        ('address', 'Address'),
        ('transaction', 'Transaction'),
    ]

    assessment_id = models.CharField(max_length=100, unique=True)
    time_of_request = models.DateTimeField(auto_now_add=True)
    response_data = JSONField()
    
    user = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE, null=True, blank=True, related_name='assessments')
    access_code = models.ForeignKey(to='users.AccessCode', on_delete=models.CASCADE, null=True, blank=True, related_name='assessments')
    type_of_assessment = models.CharField(max_length=11, choices=TYPE_CHOICES)
    address_hash = models.CharField(max_length=128, null=True, blank=True)
    transaction_hash = models.CharField(max_length=128, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)

    status_assessment = models.CharField(max_length=100, null=True)
    risk_score = models.FloatField(null=True, blank=True)
    risk_grade = models.CharField(max_length=32, null=True, blank=True)
    risk_signals = JSONField(null=True, blank=True)
    risk_volume_coin = models.FloatField(null=True, blank=True)
    risk_volume_fiat = models.FloatField(null=True, blank=True)
    assessment_updated_at = models.DateTimeField(null=True, blank=True)
    transaction_volume_coin = models.FloatField(null=True, blank=True)
    transaction_volume_fiat = models.FloatField(null=True, blank=True)
    transaction_volume_fiat_currency_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        formatted_time = self.time_of_request.strftime('%Y.%m.%d %Hh%Mm%Ss')
        return f'{formatted_time} - {self.type_of_assessment} - {self.assessment_id} - {self.status_assessment}'

    def address_hash_short(self):
        if self.address_hash:
            return self.address_hash[:5]+'...'+self.address_hash[-5:]
        else:
            return '-'

    def transaction_hash_short(self):
        if self.transaction_hash and len(self.transaction_hash) > 1:
            return self.transaction_hash[:5]+'...'+self.transaction_hash[-5:]
        else:
            return '-'

