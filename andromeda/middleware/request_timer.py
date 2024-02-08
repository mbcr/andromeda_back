from django.utils.timezone import now
import logging

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request_timing')

    def __call__(self, request):
        # Time at request start
        start_time = now()
        response = self.get_response(request)

        end_time = now()
        duration = (end_time - start_time).total_seconds()
        if duration > 0:
            self.logger.debug(f"Request to {request.path} took {duration} seconds")

        return response
