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
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    type_of_assessment = models.CharField(max_length=11, choices=TYPE_CHOICES)
    response_data = JSONField()
    status_assessment = models.CharField(max_length=100, null=True)

    def __str__(self):
        formatted_time = self.time_of_request.strftime('%Y.%m.%d %Hh%Mm%Ss')
        return f'{formatted_time} - {self.type_of_assessment} - {self.assessment_id} - {self.status_assessment}'

