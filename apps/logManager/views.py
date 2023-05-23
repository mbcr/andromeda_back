from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework import status
from rest_framework.decorators import api_view

from django.http import JsonResponse

from .models import LandingPagePipelineLog

from pprint import pprint

# Create your views here.
    
# @api_view(['GET'])
def log_landing_page_usage(request):
    import json

    def get_info_from_ip(ip_address):
        import requests

        # Imports to deal with environment variables
        import environ
        import os
        from django.conf import settings

        env = environ.Env()
        BASE_DIR = settings.BASE_DIR
        environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
        ipapi_key = env('IPAPI_KEY')
        ipgeolocation_key = env('IP_GEOLOCATION_KEY')


        def service_ipapi(ip_address):
            key = ipapi_key
            url = f'https://ipapi.co/{ip_address}/json/?key={key}'
            response = requests.get(url)
            return response.json()

        def service_ipgeolocation(ip_address):
            key = ipgeolocation_key
            url = f'https://api.ipgeolocation.io/ipgeo?apiKey={key}&ip={ip_address}'
            response = requests.get(url)
            return response.json()

        return service_ipapi(ip_address)

    if request.method == 'GET':
        log_type = request.GET['datastream']
        # Copilot, store the request's ip into a variable
        request_ip = request.META.get('REMOTE_ADDR')
        ip_data = get_info_from_ip(request_ip)
        window_data = json.loads(request.GET['window'])
        from django.conf import settings
        if settings.DEBUG:
            print('DEBUG Mode: logManager > views > log_landing_page_usage: ip_data')
            pprint(ip_data)

        try:
            new_log = LandingPagePipelineLog(
                request_ip = request_ip,
                # request_network = ip_data['network'],
                location_country = ip_data['country_name'],
                # location_region = ip_data['region'],
                location_city = ip_data['city'],
                # utc_offset = ip_data['timezone']['offset'],
                window_userAgent = window_data['userAgent'],
                window_inner_height = window_data['innerHeight'],
                window_inner_width = window_data['innerWidth'],
                log_type = log_type
            )
            new_log.save()
            return JsonResponse({'message': 'Data loaded correctly.'}, status=status.HTTP_200_OK)

        except Exception as e:
            print('Error saving LandingPagePipelineLog: ',e)
            print(f'LandingPagePipelineLog> Error accessing API. log_type: {log_type} ; ip_data: {ip_data}')
            new_log = LandingPagePipelineLog(
                request_ip = request_ip,
                window_userAgent = window_data['userAgent'],
                window_inner_height = window_data['innerHeight'],
                window_inner_width = window_data['innerWidth'],
                log_type = log_type
            )
            new_log.save()
            return JsonResponse({'message': 'Data loaded correctly.'}, status=status.HTTP_200_OK)


        



    pass
