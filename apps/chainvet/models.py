from django.db import models
from apps.users.models import CustomUser

from django.db.models import JSONField

class Assessment(models.Model):
    TYPE_CHOICES = [
        ('address', 'Address'),
        ('transaction', 'Transaction'),
    ]

    time_of_request = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    type_of_assessment = models.CharField(max_length=11, choices=TYPE_CHOICES)
    response = JSONField()

