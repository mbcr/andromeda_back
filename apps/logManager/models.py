from django.db import models
from ..users import models as userModels

# Create your models here.
class RequestEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(userModels.CustomUser, related_name='request_events', on_delete=models.SET_NULL, null=True)
    request_method = models.CharField(max_length=10)
    request_path = models.CharField(max_length=128)
    request_data = models.JSONField(blank=True, null=True)
    request_parameters = models.JSONField(blank=True, null=True)
    response_status_code = models.IntegerField(blank=True, null=True)
    request_ip = models.CharField(max_length=64,blank=True, null=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f'{self.timestamp.strftime("%Y/%m/%d %H:%M:%S")};{self.client};{self.user.first_name} {self.user.last_name};{self.request_method};{self.request_path};{self.response_status_code}'
    pass


class LandingPagePipelineLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    request_ip = models.CharField(max_length=64,blank=True, null=True)
    request_network = models.CharField(max_length=64,blank=True, null=True)
    location_country = models.CharField(max_length=128,blank=True, null=True)
    location_region = models.CharField(max_length=128,blank=True, null=True)
    location_city = models.CharField(max_length=128,blank=True, null=True)
    utc_offset = models.CharField(max_length=128,blank=True, null=True)
    window_userAgent = models.CharField(max_length=128,blank=True, null=True)
    window_inner_height = models.CharField(max_length=128,blank=True, null=True)
    window_inner_width = models.CharField(max_length=128,blank=True, null=True)

    log_type = models.CharField(max_length=128,blank=True, null=True)


    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return f'{self.timestamp.strftime("%Y/%m/%d %H:%M:%S")};{self.request_ip};{self.location_country};{self.log_type}'
    pass
