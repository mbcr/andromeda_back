from django.db import models

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

class AmountMixin:
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    amount_xmr = models.DecimalField(max_digits=20, decimal_places=8)
    amount_usd_cents = models.IntegerField(default=0)
    amount_btc = models.DecimalField(max_digits=20, decimal_places=8)


class AccountAssessment(models.Model, AmountMixin):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='assessments')
    date = models.DateTimeField()

    def __str__(self):
        return f'{self.name} - {self.date} - {self.amount}'

class DividendPayment(models.Model, AmountMixin):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='entries')
    date = models.DateTimeField()
    partner = models.CharField(max_length=100)
    unit = models.CharField(max_length=16)
    payout_address = models.CharField(max_length=100)
    tx_hash = models.CharField(max_length=100)

    def __str__(self):
        return f'Dividend payment to {self.partner} - {self.date} - {self.amount}{self.unit}'

class AccountAdjustments(models.Model, AmountMixin):
    account_to_adjust = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='adjustments')
    description = models.TextField()
    date = models.DateTimeField()

