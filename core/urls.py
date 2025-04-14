from django.urls import path
from .views import HomePageView, BookingProcedureView, ContactUsProcedureView, BookingStatsView, \
    BookingSunburstGraphView, MonthlyBookingCountView, RegisterView,LoginView,ForgotPasswordView, \
    PasswordResetConfirmView, LogoutView

urlpatterns = [
    path('get-booking-procedure-data/', BookingProcedureView.as_view(), name='get_booking_procedure_data'),
    path('get-contact-us-procedure-data/', ContactUsProcedureView.as_view(), name='get_contact_us_procedure_data'),
    path('get-booking-stats-procedure-data/', BookingStatsView.as_view(), name='get_booking_stats_procedure_data'),
    path('get-booking-count-procedure-data/', MonthlyBookingCountView.as_view(), name='get_booking_count_procedure_data'),
    path('get-booking-sunburst-procedure-data/', BookingSunburstGraphView.as_view(),
         name='get_booking_sunburst_procedure_data'),
    path('<str:url>/', HomePageView.as_view(), name='Home_page'),
    path('api/register/',RegisterView.as_view(),name='register'),
    path('api/login/',LoginView.as_view(),name='login'),
    path('api/logout/',LogoutView.as_view(),name='logout'),
    path('api/forgot-password/',ForgotPasswordView.as_view(),name='forgot_password'),
    path('api/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
