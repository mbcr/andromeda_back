from django.contrib import admin
from apps.corporate import models as corporate_models

# Register your models here.
admin.site.register(corporate_models.Account)
admin.site.register(corporate_models.AccountAssessment)
admin.site.register(corporate_models.DividendPayment)
admin.site.register(corporate_models.AccountAdjustments)

