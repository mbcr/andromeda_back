from django.db import models
from apps.users.models import CustomUser

from django.db.models import JSONField

class Assessment(models.Model):
    TYPE_CHOICES = [
        ('address', 'Address'),
        ('transaction', 'Transaction'),
    ]

    assessment_id = models.CharField(max_length=100, unique=True)
    time_of_request = models.DateTimeField(auto_now_add=True)
    response_data = JSONField()
    
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, null=True, blank=True)
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

