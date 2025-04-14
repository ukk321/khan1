from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmailTemplateView

# Create a router and register your viewset with it
router = DefaultRouter()
router.register(r'email-templates', EmailTemplateView)

# Define URL patterns for your app
urlpatterns = [
    path('email/',EmailTemplateView.as_view()),
]
