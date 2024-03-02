from django.db import models
from django.db.models import JSONField
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone as django_tz
from django.utils.crypto import get_random_string

from datetime import datetime
import logging

from apps.utilities import trocador_api, api_crystal_blockchain

class OrderAdmin(admin.ModelAdmin):
    list_filter=['created_at', 'status', 'is_paid']
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
        related_name = 'orders'
    )
    access_code = models.ForeignKey(
        'users.AccessCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'orders'
    )
    order_id = models.CharField(max_length=12, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    affiliate = models.ForeignKey(to='users.Affiliate', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    last_interaction = models.DateTimeField(auto_now=True, null=True, blank=True)
    number_of_credits = models.IntegerField(default=0)
    total_price_usd_cents = models.IntegerField(default=0)
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
    anonpay_id = models.CharField(max_length=16, null=True, blank=True)
    status_updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        paid_date = self.paid_at.strftime('%Y.%m.%d %Hh%Mm%Ss') if self.paid_at else ''
        order_by_text = f"{self.owner_type} {self.access_code if self.owner_type == 'AccessCode' else self.user}"
        paid_text = f"{paid_date if self.is_paid else self.is_paid}"
        return f'Order {self.id}.{self.order_id} - {self.created_at.strftime("%Y.%m.%d %Hh%Mm%Ss")} - {self.number_of_credits} credits - By: {order_by_text} - AnonpayID: {self.anonpay_id} - PAID: {paid_text}.'

    def generate_unique_code(self):
        length = 12
        chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            random_string = get_random_string(length, chars)
            if not Order.objects.filter(order_id=random_string).exists():
                return random_string

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_code()
        # if not self.is_paid and super(Order, self).is_paid:
        #     raise NotImplementedError('Chainvet Order save method: Missing implementation of credit attribution.')
        super(Order, self).save(*args, **kwargs)

    def update_payment_status(self): 
        if not self.anonpay_id:
            self.status_updated_at = django_tz.now()
            self.save()
            return
        try:
            trocador_status_call = trocador_api.get_trade_status(self.anonpay_id)
            trocador_status_call_data = trocador_status_call.json()
        except Exception as e:
            error_log = logging.getLogger('error_logger')
            error_log.debug(f"apps.chainvet.models>Order: Error in update_payment_status for order {str(self)}: Could not decode Trocador API into JSON.")
            return
        try:
            payment_status = trocador_status_call_data.get('Status')
            if payment_status == 'finished':
                self.is_paid = True
                self.paid_at = django_tz.now()
                self.status = 'finished'
                self.status_updated_at = django_tz.now()
                self.save()
            else:
                self.status = payment_status
                self.status_updated_at = django_tz.now()
                self.save()
        except Exception as e:
            error_log = logging.getLogger('error_logger')
            error_log.debug(f"apps.chainvet.models>Order: Error in update_payment_status for order {str(self)}: Could not update order with data: {trocador_status_call_data}.")
            return

    def minutes_since_last_update(self):
        if self.status_updated_at:
            return (django_tz.now() - self.status_updated_at).total_seconds() / 60
        else:
            return None

    def minutes_since_created(self):
        return (django_tz.now() - self.created_at).total_seconds() / 60

    def affiliate_income_share_usd_cents(self):
        if self.affiliate:
            order_margin = self.total_price_usd_cents - (80 * self.number_of_credits)
            return order_margin * self.affiliate.income_share / 10000
        else:
            return 0

class AssessmentAdmin(admin.ModelAdmin):
    list_filter = ['user', 'access_code', 'type_of_assessment']
class Assessment(models.Model):
    TYPE_CHOICES = [
        ('address', 'Address'),
        ('transaction', 'Transaction'),
    ]

    assessment_id = models.CharField(max_length=100, unique=True, db_index=True)
    time_of_request = models.DateTimeField(auto_now_add=True)
    cbc_id = models.CharField(max_length=16, null=True, blank=True)
    response_data = JSONField()
    
    user = models.ForeignKey(to='users.CustomUser', on_delete=models.CASCADE, null=True, blank=True, related_name='assessments')
    access_code = models.ForeignKey(to='users.AccessCode', on_delete=models.CASCADE, null=True, blank=True, related_name='assessments')
    type_of_assessment = models.CharField(max_length=11, choices=TYPE_CHOICES)
    address_hash = models.CharField(max_length=128, null=True, blank=True)
    transaction_hash = models.CharField(max_length=128, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    client_name = models.CharField(max_length=12, null=True, blank=True)

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
            return self.address_hash[:4]+'...'+self.address_hash[-4:]
        else:
            return '-'

    def transaction_hash_short(self):
        if self.transaction_hash and len(self.transaction_hash) > 1:
            return self.transaction_hash[:5]+'...'+self.transaction_hash[-5:]
        else:
            return '-'

    def update_assessment(self):
        error_log = logging.getLogger('error_logger')
        if self.status_assessment in ['ready']:
            return
        try:
            cbc_response = api_crystal_blockchain.check_assessment_by_id(self.assessment_id)
        except Exception as e:
            error_log.debug(f"apps.chainvet.models>Assessment: Code MAU87 Error in update_assessment for assessment {str(self)}: {e}")

        if cbc_response.get('status') == 'Error':
            error_log.debug(f"apps.chainvet.models>Assessment: Code MAU88. Error message: {cbc_response.get('message')}")
            return
        
        assessment_data = cbc_response.get('payload').get('data')[0]

        if assessment_data.get('status') not in ['ready']:
            self.assessment_updated_at = django_tz.now()
            self.save()
            return
        
        updated_at_datetime = datetime.utcfromtimestamp(assessment_data['updated_at'])
        self.assessment_updated_at = updated_at_datetime
        self.response_data = assessment_data
        self.risk_grade = assessment_data['alert_grade']
        self.risk_score = assessment_data['riskscore']
        self.risk_signals = assessment_data['signals']
        self.status_assessment = assessment_data['status']
        if self.type_of_assessment == "transaction":
            self.transaction_volume_coin = assessment_data['amount']
            self.transaction_volume_fiat = assessment_data['fiat']
            self.transaction_volume_fiat_currency_code = assessment_data['fiat_code_effective']
            self.risk_volume_coin = assessment_data['risky_volume']
            self.risk_volume_fiat = assessment_data['risky_volume_fiat']
        self.save()
