from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.transaction import atomic

#Imports for API Key Model
from django.contrib.auth import get_user_model
from rest_framework_api_key.models import AbstractAPIKey

from ..utilities.olpFunctions import OLP_Functions

from apps.chainvet.models import Order, PreOrder
from pprint import pprint


class CreditOwnerMixin:
    def set_credit_cache(self):
        owner_type = self.owner_type()
        # Credits paid for
        if owner_type == 'User':
            owner_orders = Order.objects.filter(pre_order__user = self)
        elif owner_type == 'AccessCode':
            owner_orders = Order.objects.filter(pre_order__access_code = self)
        else:
            print(f'Error: Owner type for {self} not recognised')
            return
        orders_paid_for = owner_orders.filter(is_paid=True)
        self.credits_paid_for = orders_paid_for.aggregate(models.Sum('number_of_credits'))['number_of_credits__sum'] or 0
        # Credits used
        owner_assessments = self.assessments.all().count()
        self.credits_used = owner_assessments
        # Credits available
        self.credits_available = self.credits_paid_for - self.credits_used
        # Save
        self.save()
    def create_new_order(self, pre_order:PreOrder, anonpay_details:dict):
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
    is_active = models.BooleanField(default=False)
    registration_form = models.JSONField(null=True, blank=True)

    ## Computed Fields
    credits_paid_for = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)
    credits_available = models.IntegerField(default=0)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['registration_form']

    # Functions
    def __str__(self):
        return self.email

    def number_of_api_keys(self):
        from .models import ChainVetAPIKey
        return ChainVetAPIKey.objects.filter(user=self).count()

    def number_of_valid_assessments(self):
        from ..chainvet import models as chainvet_models
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
    code = models.CharField(max_length=16, unique=True)
    start_date = models.DateTimeField(default=timezone.now)

    ## Computed Fields
    credits_paid_for = models.IntegerField(default=0)
    credits_used = models.IntegerField(default=0)
    credits_available = models.IntegerField(default=0)

    def __str__(self):
        return self.code
    
    def owner_type(self):
        return 'AccessCode'

class ChainVetAPIKey(AbstractAPIKey):
    reference = models.CharField(max_length=32, unique=True, blank=True, null=True)

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
        owner = f'User {user.email}' if user else f'AccessCode {access_code.code}'
        return f'API Key {self.reference} for {owner}'
    
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
