import datetime

from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView
from rest_framework.generics import ListAPIView,CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Page
from .serializers import CompletePageSerializer, UserRegisterSerializer,PasswordResetConfirmSerializer
from .templatetags.dashboard_graph_tags import get_sorted_contact_us, get_sorted_booking_data, get_booking_stats, \
    get_sub_service_hierarchy_data, get_monthly_booking_counts
from rest_framework import status
from utils.email_service import EmailService
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import os

User=get_user_model()

class HomePageView(ListAPIView):
    serializer_class = CompletePageSerializer
    queryset = Page.objects.all()
    allowed_methods = ('GET',)

    def get_queryset(self):
        # Retrieve the 'url' parameter from the URL path
        url = 'http://127.0.0.1:8000/' + str(self.kwargs.get('url')) + '/'

        # Use get_object_or_404 to get the Page object based on the provided URL
        page = get_object_or_404(Page, url=url)

        # Return a queryset containing only the selected Page object
        return Page.objects.filter(id=page.id)

    def list(self, request, *args, **kwargs):
        # Override list method to use the filtered queryset
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,status=200)


class BookingProcedureView(TemplateView):
    template_name = 'admin/booking_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.request.GET.get('days')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if days:
            days = int(days)
            context['data'] = get_sorted_booking_data(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            context['data'] = get_sorted_booking_data(start_time=start_date_time, end_time=end_date_time)
        else:
            context['data'] = ['No query Params Provided']
        return context

    def get(self, request, *args, **kwargs):
        days = request.GET.get('days')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if days:
            days = int(days)
            data = get_sorted_booking_data(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            data = get_sorted_booking_data(start_time=start_date_time, end_time=end_date_time)
        else:
            data = ['No query Params Provided']
        return JsonResponse(data, safe=False)


class ContactUsProcedureView(TemplateView):
    template_name = 'admin/contact_queries_table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.request.GET.get('days')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if days:
            days = int(days)
            context['data'] = get_sorted_contact_us(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            context['data'] = get_sorted_contact_us(start_time=start_date_time, end_time=end_date_time)
        else:
            context['data'] = ['No query Params Provided']
        return context

    def get(self, request, *args, **kwargs):
        days = request.GET.get('days')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if days:
            days = int(days)
            data = get_sorted_contact_us(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            data = get_sorted_contact_us(start_time=start_date_time, end_time=end_date_time)
        else:
            data = ['No query Params Provided']
        return JsonResponse(data, safe=False)


class BookingStatsView(TemplateView):
    template_name = 'admin/pie_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.request.GET.get('days')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if days:
            days = int(days)
            context['data'] = get_booking_stats(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            context['data'] = get_booking_stats(start_time=start_date_time, end_time=end_date_time)
        else:
            context['data'] = ['No query Params Provided']
        return context

    def get(self, request, *args, **kwargs):
        days = request.GET.get('days')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if days:
            days = int(days)
            data = get_booking_stats(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            data = get_booking_stats(start_time=start_date_time, end_time=end_date_time)
        else:
            data = ['No query Params Provided']
        return JsonResponse(data, safe=False)


class MonthlyBookingCountView(TemplateView):
    template_name = 'admin/bar_chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.request.GET.get('days')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if days:
            context['data'] = get_monthly_booking_counts(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            context['data'] = get_monthly_booking_counts(start_time=start_date_time, end_time=end_date_time)
        else:
            context['data'] = ['No query Params Provided']
        return context

    def get(self, request, *args, **kwargs):
        days = request.GET.get('days')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if days:
            days = int(days)
            data = get_monthly_booking_counts(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            data = get_monthly_booking_counts(start_time=start_date_time, end_time=end_date_time)
        else:
            data = ['No query Params Provided']
        return JsonResponse(data, safe=False)


class BookingSunburstGraphView(TemplateView):
    template_name = 'admin/sunburst.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        days = self.request.GET.get('days')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if days:
            days = int(days)
            context['data'] = get_sub_service_hierarchy_data(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            context['data'] = get_sub_service_hierarchy_data(start_time=start_date_time, end_time=end_date_time)
        else:
            context['data'] = None
        return context

    def get(self, request, *args, **kwargs):
        days = request.GET.get('days')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if days:
            days = int(days)
            data = get_sub_service_hierarchy_data(days=days)
        elif start_date and end_date:
            start_date_time = datetime.datetime.fromisoformat(start_date)
            end_date_time = datetime.datetime.fromisoformat(end_date)
            data = get_sub_service_hierarchy_data(start_time=start_date_time, end_time=end_date_time)
        else:
            data = {"children": []}
        return JsonResponse(data, safe=False)


def custom_404_view(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_400_view(request,exception):
    return render(request,template_name='errors/400.html',status=400)


def custom_403_view(request,exception):
    return render(request,template_name='errors/403.html',status=403)


def custom_500_view(request):
    return render(request,template_name='errors/500.html',status=500)


class RegisterView(CreateAPIView):
    serializer_class=UserRegisterSerializer

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'success': False, 'message': 'Email or password missing'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh=RefreshToken.for_user(user)
            data={
                'token':{
                    'refresh':str(refresh),
                    'access':str(refresh.access_token),
                },
                'user':{
                    'id':user.id,
                    'name':user.first_name,
                    'email':user.email
                }
            }

            return Response({'success': True, 'message': 'Login Successful','data':data }, status=status.HTTP_200_OK)

        return Response({'success': False, 'message': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt,name='dispatch')
class LogoutView(APIView):
    def post(self,request):
        try:
            refresh_token=request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    'success':False,
                    'message':'Refresh token missing',
                    'data': None},status=status.HTTP_400_BAD_REQUEST)
                
            token=RefreshToken(refresh_token)
            token.blacklist()
                
            return Response({
                    'success':True,
                    'message':'Logout Successful',
                    'data': None,
                },status=status.HTTP_200_OK)
        
        except TokenError as e:
            return Response({'success': False, 'message': str(e),'data': None}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class ForgotPasswordView(APIView):
    def post(self,request):
        email=request.data.get('email')
        try:
            user=User.objects.get(email=email)
            token=default_token_generator.make_token(user)
            uid=urlsafe_base64_encode(force_bytes(user.pk))
            base_url = os.environ.get('RESET_PASSWORD_BASE_URL', 'http://127.0.0.1:8000/')
            reset_url = f'{base_url}/reset-password?uidb64={uid}&token={token}'

            EmailService.send_email_with_template_key(
            template_key='Forgot_Password',
            recipients=[email],
            context={
                'reset_url':reset_url,
                'user':user,
            }
            )
            return Response({'success':True,'message':'Password resent email has been sent','data':user.username},status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'success':False,'message':'User does not exist','data':None},status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    return Response({'success': True,"message": "Password reset successful",'data':None}, status=status.HTTP_200_OK)
                else:
                    return Response({'success':False,"message": "Invalid token",'data':None}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({'success':False,"message": "Invalid user",'data':None}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)