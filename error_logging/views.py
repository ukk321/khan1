# Create your views here.
from rest_framework import viewsets

from error_logging.models import ErrorLog
from error_logging.serializers import ErrorLogSerializer


def simulate_error(request):
    # This view intentionally raises an exception
    raise ValueError("This is a simulated error")


class ErrorLoggerView(viewsets.ModelViewSet):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
