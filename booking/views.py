import logging
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from utils.email_service import EmailService
from booking.models import BookingModel, CancelBookingModel, PaymentModel
from booking.serializers import ClientSerializer, BookingSerializer, CancelBookingSerializer
from lacigal import settings

logger = logging.getLogger(__name__)

def extract_names(item_list, all_names):
    
    for item in item_list:
        name = item.get('name', 'Unnamed')
        all_names.append(name)
        if 'categories' in item:
            extract_names(item.get('categories', []), all_names)
        if 'sub_services' in item:
            extract_names(item.get('sub_services', []), all_names)
        if 'subservice_category' in item:
            extract_names(item.get('subservice_category', []), all_names)

class ClientView(CreateAPIView):
    serializer_class = ClientSerializer

    def post(self, request,*args,**kwargs):
        serialized_data = ClientSerializer(data=request.data)
        if serialized_data.is_valid():
            serialized_data.save()

            response = {'success': True, 'message': 'Client Created Successfully', 'data': serialized_data.data}
            return Response(response,status=status.HTTP_201_CREATED)
        else:
            response = {'success': False, 'message': 'Client Creation Failed', 'data': None}
            return Response(response,status=status.HTTP_400_BAD_REQUEST)


class ClientBookingView(CreateAPIView):
    def post(self, request,*args,**kwargs):
        client_data = request.data.get('client')
        booking_data = request.data.get('booking')

        if not client_data or not booking_data:
            return Response({
                'success': False,
                'message': 'Client and booking data are required.',
                'data':None
            },status = status.HTTP_400_BAD_REQUEST)

        client_serializer = ClientSerializer(data=client_data)
        booking_serializer = BookingSerializer(data=booking_data)

        if client_serializer.is_valid() and booking_serializer.is_valid():
            try:
                with transaction.atomic():
                    client_instance = client_serializer.save()
                    booking_instance = booking_serializer.save(client=client_instance, payment_status='ADVANCE PAID')

                    transaction_id = client_data.get('transaction_id')
                    if PaymentModel.objects.filter(transaction_id=transaction_id).exists():
                        return Response({'success': False, 'message': 'Transaction ID already exists.',
                                         },status = status.HTTP_400_BAD_REQUEST)

                    # Retrieve the booking date after saving the object
                    booking_date = booking_instance.booking_date
                    booking_id = booking_instance.booking_id

                    # Retrieve the email from the request data
                    client_email = client_instance.email_address
                    if client_email:
                        selected_items = booking_instance.selected_items

                        # Extract names of the selected items
                        selected_items_names = self.get_selected_items_names(selected_items)

                        # Construct booking details for notification
                        booking_details = {
                            'name': client_instance.name,
                            'email': client_email,
                            'selected_items': ', '.join(selected_items_names),
                            'booking_date': booking_date,
                            'payment_status': 'ADVANCE PAID',
                            'shipment_id': booking_id,
                            'phone_no': client_instance.phone_no
                        }
                        EmailService.send_email_with_template_key(
                        template_key='Order_Shipment',
                        recipients=[client_email],
                        context=booking_details)

                        EmailService.send_email_with_template_key(
                        template_key='Shipment_Admin',
                        recipients=[settings.ADMINS[0][1]],
                        context=booking_details)

                    data={
                        'client_data': client_serializer.data,
                        'booking_data': booking_serializer.data}

                    response = {
                        'success': True,
                        'message':'Booking Created Successfully',
                        'data':data
                    }
                    return Response(response,status = status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': str(e),
                    'data':None
                },status= status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            errors = {
                'client_errors': client_serializer.errors if not client_serializer.is_valid() else {},
                'booking_errors': booking_serializer.errors if not booking_serializer.is_valid() else {}
            }
            return Response({
                'success': False,
                'message': errors,
                'data':None
            },status= status.HTTP_400_BAD_REQUEST)

    def get_selected_items_names(self, selected_items):
        services = selected_items.get('services', [])
        deals = selected_items.get('deals', []) if 'deals' in selected_items else []
        all_names = []

        if services:
            extract_names(services, all_names)
        if deals:
            extract_names(deals, all_names)

        return all_names


class SendOTP(CreateAPIView):
    def post(self, request,*args,**kwargs):
        serializer = CancelBookingSerializer(data=request.data)
        booking_id = request.data.get('booking_id')
        contact_no = request.data.get('contact_number')

        if not booking_id or not contact_no:
            return Response({'success':False,'message': 'Booking ID and contact number are required.','data':None},
                            status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            try:
                booking = BookingModel.objects.get(booking_id=booking_id, client__phone_no=contact_no)
                client = booking.client

                # Ensure contact number matches the client's registered number
                if client.phone_no != contact_no:
                    return Response({'success':False,'message': 'Contact number does not match the registered number.','data':None},
                                    status=status.HTTP_400_BAD_REQUEST)

                cancel_booking = serializer.save(
                    created_by=request.user if request.user.is_authenticated else User.objects.get(username='system'),
                    client=client,
                    booking=booking  # Ensure the booking is correctly set
                )

                # Send email notification
                client_email = client.email_address
                if client_email:
                    selected_items = booking.selected_items

                    # Extract names of the selected items
                    selected_items_names = self.get_selected_items_names(selected_items)

                    booking_details = {
                        'selected_items': ', '.join(selected_items_names),
                        'client_name': client.name,
                        'shipment_id': booking.booking_id,
                        'otp': cancel_booking.otp,
                        'contact_no': contact_no,
                    }

                    EmailService.send_email_with_template_key(
                        template_key='Shipment_OTP',
                        recipients=[client_email],
                        context=booking_details
                    )

                    return Response({'success':True,'message': 'OTP sent successfully. Please check your email.','data':serializer.data},
                                    status=status.HTTP_201_CREATED)
            except BookingModel.DoesNotExist:
                return Response({'success':False,'message': 'Booking not found.','data':None}, status=status.HTTP_404_NOT_FOUND)
        return Response({'success':False,'message': 'Invalid request data.','data':None}, status=status.HTTP_400_BAD_REQUEST)

    def get_selected_items_names(self, selected_items):
        services = selected_items.get('services', [])
        deals = selected_items.get('deals', []) if 'deals' in selected_items else []
        all_names = []

        if services:
            extract_names(services, all_names)
        if deals:
            extract_names(deals, all_names)

        return all_names


class CancelBooking(CreateAPIView):
    def post(self, request,*args,**kwargs):
        booking_id = request.data.get('booking_id')
        user_otp = request.data.get('otp')

        if not booking_id or not user_otp:
            return Response( {'success':False,'message': 'Booking ID and OTP are required.','data':None}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = get_object_or_404(BookingModel,booking_id=booking_id)

            # Retrieve the cancellation record by joining on the booking
            cancel_booking = CancelBookingModel.objects.get(booking=booking, otp=user_otp)

        except Exception as e:
            return Response({'error: Exception Occurred:'},e)
        except CancelBookingModel.DoesNotExist:
            return Response({'error': 'Invalid Booking ID or OTP.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the booking is already cancelled to prevent re-cancellation
        if cancel_booking.booking.booking_status == 'CANCELLED':
            return Response({'error': 'Booking is already cancelled.'}, status=status.HTTP_409_CONFLICT)

        try:
            with transaction.atomic():
                # Update the booking status to 'Cancelled'
                cancel_booking.booking.booking_status = 'CANCELLED'
                cancel_booking.booking.save()

                selected_items = booking.selected_items
                selected_items_names = self.get_selected_items_names(selected_items)

                # Send email notification
                client_email = cancel_booking.client.email_address if cancel_booking.client else 'default_email@example.com'
                booking_details = {
                    'client_name': cancel_booking.client.name if cancel_booking.client else 'No Name',
                    'shipment_id': booking_id,
                    'status': 'Cancelled',
                    'otp': user_otp,
                    'contact_no': cancel_booking.contact_no,
                    'selected_items': ', '.join(selected_items_names)
                }
                EmailService.send_email_with_template_key(
                    template_key='Shipment_Cancellation',
                    recipients=[client_email],
                    context=booking_details
                )

                return Response({'success':True,'message': 'Booking cancelled successfully.','data':None}, status=status.HTTP_200_OK)

        except Exception as e:
            # Handle unexpected errors
            return Response( {'success':False,'message': str(e),'data':None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_selected_items_names(self, selected_items):
        services = selected_items.get('services', [])
        deals = selected_items.get('deals', []) if 'deals' in selected_items else []
        all_names = []

        if services:
            extract_names(services, all_names)
        if deals:
            extract_names(deals, all_names)

        return all_names


class GetBooking(ListAPIView):
    serializer_class = BookingSerializer
    queryset = BookingModel.objects.all()

    def get_queryset(self):
        booking_id = self.request.query_params.get('booking_id')
        contact_number = self.request.query_params.get('contact_number')

        if not booking_id or not contact_number:
            return BookingModel.objects.none()

        # Ensure the contact number retains the + sign and remove whitespace
        contact_number = contact_number.strip().replace(" ", "")

        # Ensure the contact number starts with '+'
        if not contact_number.startswith('+'):
            contact_number = '+' + contact_number

        queryset = BookingModel.objects.filter(booking_id=booking_id, client__phone_no=contact_number)

        if not queryset.exists():
            return BookingModel.objects.none()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({'success':False,'message': 'Booking not found.','data':None}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)