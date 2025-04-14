from django.urls import path, include

from .views import simulate_error, ErrorLoggerView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'error-logging', ErrorLoggerView, basename='error_logging_fe')

urlpatterns = [
    path('simulate-error/', simulate_error, name='simulate_error'),
    path('api/', include(router.urls)),
]
