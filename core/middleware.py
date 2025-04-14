from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin


class AdminRedirectMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == reverse('admin:index') and request.user.is_authenticated:
            if request.user.groups.filter(name='Admin Staff').exists():
                return redirect(reverse('admin:booking_bookingmodel_changelist'))
        return None
