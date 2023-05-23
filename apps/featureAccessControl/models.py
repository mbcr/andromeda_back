from django.db import models

from ..users.models import CustomUser
# from ..corporate.models import Corporate


class FeatureAccessCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='feature_access_codes_created_by_custom_user', null=True, blank=True)

    def __str__(self):
        return self.code

class Authorisation(models.Model):
    feature_code = models.ForeignKey(FeatureAccessCode, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='authorisations')
    # company = models.ForeignKey(Corporate, on_delete=models.CASCADE, blank=True, null=True, related_name='authorisations')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='authorisations_created_by_custom_user', blank=True, null=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(user__isnull=False), name='one_field_is_null')
        ]
    
    def __str__(self):
        return f'{self.feature_code} for {self.user}'

    def delete(self):
        self.active = False
        self.save()

