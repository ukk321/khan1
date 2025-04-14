from django.urls import path

from booking.views import ClientView, SendOTP, GetBooking, CancelBooking, ClientBookingView

urlpatterns = [
    path('client_booking/', ClientView.as_view(), name='bookings_for_client'),
    path('get-booking/', GetBooking.as_view(), name='retrieve-booking'),
    path('send-otp/', SendOTP.as_view(), name='send_otp_mail'),
    path('cancel-booking/', CancelBooking.as_view(), name='verify_cancel_booking'),
    path('construct-booking/', ClientBookingView.as_view(), name='client-booking')
]
