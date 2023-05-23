'''Aggregates all handlers for the log manager. Any interaction with the models should be done through these handlers.'''

import json
from .models import RequestEvent
from pprint import pprint

def get_client_ip(request):
    '''Returns the IP address of the request.'''
    # Ref.: https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_request(request,response_code):
    '''Logs a request to the database.'''
    client = request.user.corporate_group

    # RequestEvent.objects.create(
    #     client=client,
    #     user=request.user,
    #     request_method=request.method,
    #     request_path=request.path,
    #     request_data=request.data,
    #     request_parameters=request.query_params,
    #     response_status_code=response_code,
    #     request_ip=get_client_ip(request)
    # ) <--- It is better to use the below method so errors are identified by field.

    new_event = RequestEvent()
    new_event.client = client
    new_event.user = request.user
    new_event.request_method = request.method
    new_event.request_path = request.path
    new_event.request_data = request.data
    new_event.request_parameters = request.query_params
    new_event.response_status_code = response_code
    new_event.request_ip = get_client_ip(request)
    new_event.save()

    return None