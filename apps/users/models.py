from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.transaction import atomic
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

#Imports for API Key Model
from django.contrib.auth import get_user_model
from rest_framework_api_key.models import AbstractAPIKey

from ..utilities.olpFunctions import OLP_Functions
from apps.chainvet.models import Order, Assessment
from apps.utilities import api_crystal_blockchain as cbc_api

from pprint import pprint
import logging
import requests
from datetime import datetime
from coinpaprika.client import Client as CoinpaprikaClient


def get_price_in_usd_cents(number_of_credits:int):
    def get_volume_discount(number_of_credits:int):
        # if number_of_credits <= 5:
        #     return 0
        # elif number_of_credits <= 10:
        #     return 0.0909
        # elif number_of_credits <= 20:
        #     return 0.15
        # elif number_of_credits <= 50:
        #     return 0.20
        # elif number_of_credits <= 100:
        #     return 0.25
        # else:
        #     return 0.30
        # base_price_per_credit_in_usd_cents = 220
        # total_price_in_usd_cents = number_of_credits * base_price_per_credit_in_usd_cents * (1-get_volume_discount(number_of_credits))
        pass
    # Migrate price management to DB
    # 5 - $11
    # 10 - $20
    # 25 - $40
    # 50 - $70
    # 100 - $120
    # 500 - $550
    # 1000 - $990
    package_options = {
        5: 1100,
        10: 2000,
        25: 4000,
        50: 7000,
        100: 12000,
        # 500: 55000,
        500: 50000,
        # 1000: 99000,
        1000: 90000
    }
    if number_of_credits in package_options:
        total_price_in_usd_cents = package_options.get(number_of_credits)
        return total_price_in_usd_cents
    else:
        raise Exception(f'Error: Number of credits requested ({number_of_credits}) is not recognised as a package option. The current options are: [5, 10, 25, 50, 100, 500, 1000]')

def coin_name_transfer_function(coin_name:str): # TO BE IMPLEMENTED BETWEEN WHAT IS RECEIVED FROM THE API OR FRONTEND AND WHAT COINPAPRIKA EXPECTS
    return coin_name

def fetch_price_in_crypto(price_in_usd_cents:int, payment_coin_paprika_name:str):
    coinpaprika_client = CoinpaprikaClient()
    try:
        conversion_payload = coinpaprika_client.price_converter(base_currency_id='usd-us-dollars', quote_currency_id=payment_coin_paprika_name, amount=price_in_usd_cents/100)
        price_in_crypto = conversion_payload.get('price')
    except Exception as e:
        error_logger = logging.getLogger('error_logger')
        error_logger.debug(f'apps.users.models.fetch_price_in_crypto: Error fetching price in crypto for {price_in_usd_cents} USD cents and {payment_coin_paprika_name} as payment coin. Error: {e}')
        raise Exception(f'Error fetching price in crypto for {price_in_usd_cents} USD cents and {payment_coin_paprika_name} as payment coin. Error: {e}')
    
    return price_in_crypto

def fetch_payment_address_and_memo(payment_coin:str, payment_network:str):
    if payment_coin == 'Monero' and payment_network == 'XMR':
        payment_coin = coin_name_transfer_function('xmr-monero') 
        payment_address = '8883ZWu66QEAM1kjCSvotjWYJtvmHEZcR85E3qF9huoe91emTeFnD6jNBQjk6sNtFVD8GriRFJXntWT1mXQDjEYBN85fPk3' 
        payment_memo = '' 
    elif payment_coin == 'usdt' and payment_network == 'trc20':
        payment_coin = coin_name_transfer_function('usdt-tether')
        payment_address = 'TB79az7fMt1L774Mg8BhDNdWxqaV1jP1X2'
        payment_memo = '' 
    else:
        raise Exception(f'Payment coin and network combination not recognised: {payment_coin} - {payment_network}. Only Monero with XMR network and usdt with trc20 network are currently supported.')
    
    return {
        'payment_coin': payment_coin,
        'payment_address': payment_address,
        'payment_memo': payment_memo,
    }

class CreditOwnerMixin:
    def set_credit_cache(self): # Sets the computed fields for a credit owner instance (CustomUser or AccessCode)
        owner_type = self.owner_type()
        # Credits paid for
        if owner_type == 'User':
            owner_orders = Order.objects.filter(user = self)
        elif owner_type == 'AccessCode':
            owner_orders = Order.objects.filter(access_code = self)
        else:
            print(f'Error: Owner type for {self} not recognised')
            return
        if not owner_orders.exists():
            self.credits_paid_for = 0
            self.credits_used = 0
            self.credits_available = 0
            self.save()
            import logging
            error_logger = logging.getLogger('error_logger')
            error_logger.debug(f'apps.users.models.CreditOwnerMixin.set_credit_cache: No orders found for {str(self)} to set credit cache.')
            return 0
        orders_paid_for = owner_orders.filter(is_paid=True)
        self.credits_paid_for = orders_paid_for.aggregate(models.Sum('number_of_credits'))['number_of_credits__sum'] or 0
        # Credits used
        owner_assessments = self.assessments.all().count()
        self.credits_used = owner_assessments
        # Credits available
        self.credits_available = self.credits_paid_for - self.credits_used
        # Save
        self.save()
        return self.credits_available
    def create_new_order_v0(self, anonpay_details:dict):
        new_order, created = Order.objects.get_or_create(
            pre_order=pre_order,
            number_of_credits=pre_order.number_of_credits,
            total_price_usd_cents=pre_order.total_price_usd_cents,
            payment_coin=pre_order.payment_coin,
            payment_network=pre_order.payment_network,
            total_price_crypto=anonpay_details['total_price_crypto'],
            payment_is_direct=anonpay_details['payment_is_direct'],
            payment_address=anonpay_details['payment_address'],
            payment_memo=anonpay_details['payment_memo'],
            swap_details=anonpay_details['swap_details'],
        )
        if not created:
            print(f'Order already exists for {pre_order}')
    def create_new_order_v1(self, number_of_credits:int, payment_coin:str, payment_network:str, affiliate=None):
        owner_type = self.owner_type()
        try:
            price = get_price_in_usd_cents(number_of_credits)
        except Exception as e:
            raise Exception(f'Error fetching price for {number_of_credits} credits. {e}')
        payment_info = fetch_payment_address_and_memo(payment_coin,payment_network)
        price_in_crypto = fetch_price_in_crypto(price, payment_info.get('payment_coin'))
        try:
            new_order = Order.objects.create(
                owner_type=owner_type,
                user = self if owner_type == 'User' else None,
                access_code = self if owner_type == 'AccessCode' else None,
                affiliate = affiliate,
                number_of_credits = number_of_credits,
                total_price_usd_cents = price,
                payment_coin = payment_coin,
                payment_network = payment_network,
                total_price_crypto = price_in_crypto,
                payment_is_direct = False,
                payment_address = payment_info.get('payment_address'),
                payment_memo = payment_info.get('payment_memo'),
                status = 'Pending',
            )
            new_order.save()
        except Exception as e:
            raise Exception(f'Error creating new order for {self} with data: {number_of_credits} credits, {payment_coin} payment coin, {payment_network} payment network. Error: {e}')
        return new_order
    def assign_credits_to_api(self, api_key: 'ChainVetAPIKey', number_of_credits:int):
        if api_key.revoked:
            print(f"Error: API Key {api_key} is revoked, and therefore it can't be used anymore.")
            return
        if self.credits_available < number_of_credits:
            print(f'Error: Not enough credits available for {self} ({self.credits_available}) to assign {number_of_credits} to {api_key}')
            return
        def self_is_api_key_owner():
            api_key_owner_type = api_key.owner_type
            if api_key_owner_type == 'User':
                api_owner = api_key.user
            elif api_key_owner_type == 'AccessCode':
                api_owner = api_key.access_code
            else:
                print(f'Error: Owner type for {api_key} not recognised')
                return
            return api_owner == self
        if not self_is_api_key_owner():
            print(f'Error: {self} is not the owner of {api_key}, and therefore cannot assign credits to it.')
            return
        with atomic():
            self.credits_available -= number_of_credits
            api_key.assigned_credits += number_of_credits
            self.save()
            api_key.save()
    def create_new_assessment(self, assessment_type:str, address:str, currency:str, tx_hash:str=None, override_existing_assessment:bool=False):
        def assessment_already_exists(cbc_request_data: dict) -> bool:
            if assessment_type == "address":
                request_transaction_hash = None
            else:
                request_transaction_hash = cbc_request_data['tx']
            assessment_query = Assessment.objects.filter(type_of_assessment=assessment_type,address_hash=cbc_request_data['address'],currency=cbc_request_data['currency'])
            if assessment_type == "transaction":
                assessment_query = assessment_query.filter(transaction_hash=request_transaction_hash) 
            assessment_query_for_owner = assessment_query.filter(access_code = self) if self.owner_type() == 'AccessCode' else assessment_query.filter(user = self)
            existing_assessment = assessment_query_for_owner.first()

            if existing_assessment:
                return True, existing_assessment
            else:
                return False, None
        def generate_unique_code(length:int=12):
            chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
            return get_random_string(length, chars)

        error_logger = logging.getLogger('error_logger')
        # Parameter checks
        if assessment_type not in ['address', 'transaction']:
            return {
                'status': 'Error',
                'message': f"Error: assessment_type must be either 'address' or 'transaction'. Value provided = {assessment_type}"
            }

        # Check if there are enough credits available
        available_credits = self.set_credit_cache()
        if available_credits < 1:
            payload = {
                'status': 'Error',
                'message': f'Not enough credits available for {str(self)} to create a new assessment.'
            }
            return payload
        # Set name based on owner type
        if self.owner_type() == 'User':
            name = generate_unique_code(length=12)
        elif self.owner_type() == 'AccessCode':
            name = generate_unique_code(length=12)
        else:
            return {
                'status': 'Error',
                'message': f'Owner type for {self} not recognised'
            }
        
        # Check if tx data is provided
        if assessment_type == 'transaction':
            if not tx_hash:
                return {
                    'status': 'Error',
                    'message': f'No transaction hash provided for transaction assessment.'
                }

        # Prepare the request data for the CBC API
        if assessment_type == "address":
            direction = "withdrawal"
            cbc_request_data = {
                "direction": direction,
                "address": address,
                "name": name,
                "currency": currency
            }
        else:
            direction = "deposit"
            tx = tx_hash
            cbc_request_data = {
                "direction": direction,
                "address": address,
                "tx": tx,
                "name": name,
                "currency": currency                
            }

        # Check if assessment already exists
        assessment_exists, existing_assessment = assessment_already_exists(cbc_request_data)
        if assessment_exists and not override_existing_assessment:
            return {
                'status': 'Warning',
                'payload': AssessmentListSerializer(existing_assessment).data,
                'message': f'Assessment already exists for the requested data. The API parameter override_existing_assessment default value is false. Your request had it set to {override_existing_assessment} so a new assessment was not created.'
            }
        
        # Make the request to the CBC API
        try:
            response = cbc_api.new_assessment(cbc_request_data)
            if response.get('status') == 'Error':
                raise Exception(f'Error creating new assessment for {str(self)} with data: {cbc_request_data}. Error message: {response.get("message")}')
            response_data = response.get('data')
        except Exception as e:
            error_logger.debug(f'apps.users.models.CreditOwnerMixin.create_new_assessment: Error creating new assessment for {str(self)} after CBC request, with data: {cbc_request_data}. Error: {e}')
            raise Exception(f'Error creating new assessment for {str(self)} with data: {cbc_request_data}. Exception: {e}')

        # Initiate atomic transaction to ensure the client is only charged if the assessment is successfully created
        try:
            with atomic():
                available_credits -= 1
                self.api_credits = available_credits
                self.save()
                updated_at_datetime = datetime.utcfromtimestamp(response_data['data']['updated_at'])
                new_assessment = Assessment(
                    assessment_updated_at = updated_at_datetime,
                    currency = currency,
                    address_hash = address,
                    type_of_assessment = "address",
                    response_data = response_data,
                    risk_grade = response_data['data']['alert_grade'],
                    risk_score = response_data['data']['riskscore'],
                    risk_signals = response_data['data']['signals'],
                    status_assessment = response_data['data']['status'],
                    assessment_id = response_data['data']['id'],
                    client_name = name,
                )
                if self.owner_type() == 'User':
                    new_assessment.user = self
                else:
                    new_assessment.access_code = self
                if assessment_type == "transaction":
                    new_assessment.type_of_assessment = "transaction"
                    new_assessment.transaction_hash = tx
                    new_assessment.transaction_volume_coin = response_data['data']['amount']
                    new_assessment.transaction_volume_fiat = response_data['data']['fiat']
                    new_assessment.transaction_volume_fiat_currency_code = response_data['data']['fiat_code_effective']
                    new_assessment.risk_volume_coin = response_data['data']['risky_volume']
                    new_assessment.risk_volume_fiat = response_data['data']['risky_volume_fiat']
                new_assessment.save()
            from apps.chainvet.serializers import AssessmentListSerializer
            return {
                'status': 'Success',
                'payload': AssessmentListSerializer(new_assessment).data,
            }
        except Exception as e:
            error_logger.debug(f'apps.users.models.CreditOwnerMixin.create_new_assessment: Code UJ56D Error creating new assessment for {str(self)} after CBC request, with data: {cbc_request_data}. Error: {e}')
            return {
                'status': 'Error',
                'message': f'Error creating new assessment for {str(self)} with data: {cbc_request_data}. Error code HJG87: {e}'
            }

        # Prepare response payload
        payload = {
            "user_remaining_credits": available_credits,
            "type": "address",
            "hash": address,
            "assessment_status": response_data['data']['status'],
            "risk_grade": response_data['data']['alert_grade'],
            "risk_score": response_data['data']['riskscore'],
            "risk_signals": response_data['data']['signals']
        }
        if assessment_type == "transaction":
            payload['type'] = "transaction"
            payload['transaction_hash'] = tx
            payload['risk_volume_coin'] = response_data['data']['risky_volume']
            payload['risk_volume_fiat'] = response_data['data']['risky_volume_fiat']
            payload['risk_volume_fiat_currency_code'] = response_data['data']['fiat_code_effective']

        # If here, the assessment was successfully created. Return payload
        return {
            'status': 'Success',
            'message': f'New Assessment created for client {str(self)} with data: {cbc_request_data}',
            'payload': payload
        }
    def create_new_api_key(self, reference:str=None):
        if len(reference) > 32:
            return {
                'status': 'Error',
                'message': f"API Key reference '{reference}' is too long. Maximum length is 32 characters."
            }
        owner_type = self.owner_type()
        new_api_key, key = ChainVetAPIKey.objects.create_key(
            reference = reference,
            name=reference,
            owner_type = owner_type,
            user = self if owner_type == 'User' else None,
            access_code = self if owner_type == 'AccessCode' else None,
            shares_credits_with_owner = True,
        )
        return {
            'status': 'Success',
            'message': f"New API Key created for {owner_type} {self}.",
            'api_key_reference': new_api_key.reference,
            'api_key': key
        }

class CustomAccountManager(BaseUserManager):
    
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        # #Create Person object associated with this superuser
        # This functions calls create_user, which is already creating an associated Person

        return self.create_user(email, password, **other_fields)

    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))

        # organisation = other_fields.get('registration_form')
        # organisation_type = organisation['organisation_type']
        # new_organisation = create_new_organisation(organisation)

        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.is_active = True
        
        #Save user and associated person
        user.save()
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin, CreditOwnerMixin):
    email = models.EmailField(_('email address'), unique=True)
    start_date = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    registration_form = models.JSONField(null=True, blank=True)
    affiliate_origin = models.OneToOneField('users.Affiliate', on_delete=models.SET_NULL, null=True, blank=True)

    ## Computed Fields
    credits_paid_for = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)
    credits_available = models.IntegerField(default=0)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['registration_form']

    # Functions
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        # Check if the Affiliate already exists to avoid duplication
        if not hasattr(self, 'affiliate'):
            Affiliate.objects.create(user=self)

    def number_of_api_keys(self):
        from .models import ChainVetAPIKey
        return ChainVetAPIKey.objects.filter(user=self).count()

    def number_of_valid_assessments(self):
        from apps.chainvet import models as chainvet_models
        return chainvet_models.Assessment.objects.filter(user=self).count()

    def owner_type(self):
        return 'User'


    ## Object level permission management functions
    def set_tier(self, tier):
        from scripts.feature_access_control import set_tier_for_target
        set_tier_for_target(self, tier)
    def tier(self):
        from scripts.feature_access_control import Tier_1, Tier_2
        tier_1_access_count = len(Tier_1().access_codes)
        tier_2_access_count = len(Tier_2().access_codes)
        user_s_authorisations = self.authorisations.all().filter(active=True)
        authorisations_count = user_s_authorisations.count()
        if authorisations_count > (tier_2_access_count+5):
            return 3
        if authorisations_count > (tier_1_access_count):
            return 2
        if authorisations_count == tier_1_access_count:
            return 1
        return 0    
    def add_to_group(self, group_name):
        from django.contrib.auth.models import Group
        group = Group.objects.get(name=group_name)
        self.groups.add(group)

class AccessCode(models.Model, CreditOwnerMixin):
    code = models.CharField(max_length=16, unique=True, db_index=True)
    start_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(null=True, blank=True)
    affiliate_origin = models.ForeignKey('users.Affiliate', on_delete=models.SET_NULL, null=True, blank=True)

    ## Computed Fields
    credits_paid_for = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)
    credits_available = models.IntegerField(default=0)

    def __str__(self):
        return self.code
    
    def generate_unique_code(self):
        length = 16
        chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            code = get_random_string(length, chars)
            if not AccessCode.objects.filter(code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super(AccessCode, self).save(*args, **kwargs)

    def owner_type(self):
        return 'AccessCode'

class ChainVetAPIKey(AbstractAPIKey):
    reference = models.CharField(max_length=32, blank=True, null=True)

    class OwnerType(models.TextChoices):
        USER = 'User', 'User'
        ACCESSCODE = 'AccessCode', 'AccessCode'
    owner_type = models.CharField(
        max_length=10,
        choices=OwnerType.choices,
        default=OwnerType.USER,
    )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="api_keys",
        null=True,
        blank=True
    )
    access_code = models.ForeignKey(
        AccessCode,
        on_delete=models.CASCADE,
        related_name="api_keys",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(blank=True, null=True)

    shares_credits_with_owner = models.BooleanField(default=False)
    assigned_credits = models.IntegerField(default=0)
    
    def __str__(self):
        if self.owner_type == 'User':
            user = self.user
            owner = f'User {user.email}'
        elif self.owner_type == 'AccessCode':
            access_code = self.access_code
            owner = f'AccessCode {access_code.code}'
        else:
            owner = 'Unknown'
        return f"API Key '{self.reference}' for {owner} - ({self.hashed_key[:5]}...{self.hashed_key[-5:]})"

    def revert_credits_to_owner(self):
        if self.shares_credits_with_owner:
            owner = self.user if self.owner_type == 'User' else self.access_code
            with atomic():
                owner.credits_available += self.assigned_credits
                self.assigned_credits = 0
                self.shares_credits_with_owner = False
                owner.save()
                self.save()

class ClientLog(models.Model):
    class OwnerType(models.TextChoices):
        USER = 'User', 'User'
        ACCESSCODE = 'AccessCode', 'AccessCode'
    owner_type = models.CharField(
        max_length=10,
        choices=OwnerType.choices,
        default=OwnerType.USER,
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="client_logs",
        null=True,
        blank=True
    )
    access_code = models.ForeignKey(
        AccessCode,
        on_delete=models.CASCADE,
        related_name="client_logs",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ip_log = models.CharField(max_length=32, blank=True, null=True)
    user_agent = models.CharField(max_length=128, blank=True, null=True)
    device_info = models.JSONField(null=True, blank=True)

class Affiliate(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='affiliate')
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    affiliate_code = models.CharField(max_length=8, unique=True, blank=True, null=True)
    income_share = models.IntegerField(default=5000) # 1/100 parts: 5000 = 50.00%

    def generate_unique_code(self):
        length = 8
        chars = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789'
        while True:
            code = get_random_string(length, chars)
            if not Affiliate.objects.filter(affiliate_code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.affiliate_code:
            self.affiliate_code = self.generate_unique_code()
        super(Affiliate, self).save(*args, **kwargs)
    
    def __str__(self):
        return f'Affiliate {self.affiliate_code}'


class ConfigVariable(models.Model):
    name = models.CharField(max_length=32, null=True, blank=True)
    value = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"{self.name}: {self.value}"



