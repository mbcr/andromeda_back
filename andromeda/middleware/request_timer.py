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
            print(f"Request to {request.path} took {duration} seconds")
            self.logger.debug(f"Request to {request.path} took {duration} seconds")
        
        print(f"Logger Level: {self.logger.getEffectiveLevel()}")
        # Iterate over all handlers of the logger
        for handler in self.logger.handlers:
            print(f"Handler: {handler.__class__.__name__}")
            if hasattr(handler, 'baseFilename'):
                print(f"File Path: {handler.baseFilename}")

        return response
