import traceback

from django.db import models
from django.http import HttpResponseServerError

from .models import ErrorLog


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            # Log the exception
            self.log_exception(request, e)
            # Return a 500 Internal Server Error response
            return HttpResponseServerError("Internal Server Error")
        return response

    def log_exception(self, request, exception):
        # Create an instance of the ErrorLog model and save it
        ErrorLog.objects.create(
            level="Error",
            message=str(exception),
            stack_trace=traceback.format_exc(),
            request_path=request.path,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            method=request.method,
            status_code=500,
            request_time=models.DateTimeField(auto_now_add=True),
            request_method=request.method
        )

