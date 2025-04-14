import os

import django

from booking.serializers import ClientSerializer, BookingSerializer, PaymentSerializer, CancelBookingSerializer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lacigal.settings')
django.setup()

import datetime
from email_templates.models import EmailTemplate
from rest_framework.test import APITestCase
from booking.models import ClientModel, BookingModel, generate_unique_booking_id, PaymentModel, CancelBookingModel


# Create your tests here.


class BookingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Objects created here are committed and visible to all test methods
        EmailTemplate.objects.create(
            templates="Booking_Confirmation",
            subject="Testing Payment Template",
            body="Testing Payment Template On Payment Model Save."
        )

        cls.cancel_booking_otp = '901739'

    def setUp(self):
        self.client_model_instance = ClientModel.objects.create(
            name="Abdul",
            email_address="alvi11225@gmail.com",
            phone_no="+923030709406",
        )

        self.client_model_update_instance = ClientModel.objects.filter(id=self.client_model_instance.id).update(
            name="Abdul Rehman",
            email_address="alvi11225@gmail.com",
            phone_no="+923030709406",
        )

        self.client_model_update_instance = ClientModel.objects.get(id=self.client_model_instance.id)

        self.booking_date = datetime.date.today() + datetime.timedelta(days=5)
        self.arrival_time = datetime.time(9, 30)
        self.end_time = datetime.time(10, 30)
        self.booking_id = generate_unique_booking_id()
        self.json_booking_items = {
            "booking": {
                "booking_date": f'{self.booking_date}',
                "payment_status": "PAID",
                "total_price": 5000,
                "selected_items": {
                    "services": [
                        {
                            "id": 54,
                            "name": "Hair",
                            "categories": [
                                {
                                    "id": 25,
                                    "name": "Hair Cut",
                                    "sub_services": [
                                        {
                                            "id": 79,
                                            "name": "Signature Cut",
                                            "heading": "Signature Cut",
                                            "currency": "PKR",
                                            "description": "Transform your look with our premium signature haircut.",
                                            "discounted_price": "0.00",
                                            "image": "https://lacigal-assets.s3.amazonaws.com/image-350x175_10.jpg",
                                            "no_of_persons": 1,
                                            "parentName": "Hair Cut",
                                            "price": 5000,
                                            "subservice_category": []
                                        }
                                    ]
                                }
                            ],
                            "description": "Experience Precision Cuts, Stunning Colors, and Luxurious Treatments at LA-CIGAL Salon & Spa. Our Expert Stylists Provide Personalized Care Tailored to Enhance Your Natural Beauty. Discover Your Perfect Look Today. Book Your Appointment and Step into a World of Renewed Confidence and Style."
                        }
                    ]
                }
            }
        }
        self.booking_model_instance = BookingModel.objects.create(
            client=self.client_model_instance,
            booking_date=self.booking_date,
            arrival_time=self.arrival_time,
            end_time=self.end_time,
            payment_status='PAID',
            selected_items=self.json_booking_items,
            booking_id=self.booking_id,
            booking_status="BOOKED",
            total_price=50000,
            is_deal=False,
        )

        self.booking_date_update = datetime.date.today() + datetime.timedelta(days=7)
        self.arrival_time_update = datetime.time(10, 30)
        self.end_time_update = datetime.time(11, 30)

        self.booking_model_update_instance = BookingModel.objects.filter(id=self.booking_model_instance.id).update(
            client=self.client_model_instance,
            booking_date=self.booking_date_update,
            arrival_time=self.arrival_time_update,
            end_time=self.end_time_update,
            payment_status='ADVANCE PAID',
            selected_items=self.json_booking_items,
            booking_id=self.booking_id,
            booking_status="COMPLETED",
            total_price=500000,
            is_deal=False,
        )

        self.booking_model_update_instance = BookingModel.objects.get(id=self.booking_model_instance.id)

        self.payment_model_instance = PaymentModel.objects.create(
            payment_status='PAID',
            payment_mode='JAZZCASH',
            transaction_id='123456789012',
            booking=self.booking_model_instance,
            remaining_payment=0
        )

        self.payment_model_update_instance = PaymentModel.objects.filter(id=self.payment_model_instance.id).update(
            payment_status='ADVANCE PAID',
            payment_mode='CASH',
            transaction_id='123456789000',
            booking=self.booking_model_instance,
            remaining_payment=0
        )

        self.payment_model_update_instance = PaymentModel.objects.get(id=self.payment_model_instance.id)

        self.booking_cancel_booking_model = CancelBookingModel.objects.create(
            booking=self.booking_model_instance,
            client=self.client_model_instance,
            contact_no="+923030709406",
        )

        self.booking_cancel_booking_update_model = CancelBookingModel.objects.filter(
            id=self.booking_cancel_booking_model.id).update(
            booking=self.booking_model_instance,
            client=self.client_model_instance,
            contact_no="+923030709406",
        )

        self.booking_cancel_booking_update_model = CancelBookingModel.objects.get(
            id=self.booking_cancel_booking_model.id)

        # Create some data to test with
        self.client_data = {
            'name': 'John Doe',
            'email_address': 'john@example.com',
            'phone_no': '+923030709406'
        }

        self.booking_data = {
            'client': 1,
            'date': '2024-09-06',
            'time': '14:00',
            'service': 'Massage'
        }

        self.payment_data = {
            'booking': 1,
            'amount': 100.0,
            'payment_date': '2024-09-06',
            'payment_method': 'Credit Card'
        }

        self.cancel_booking_data = {
            'contact_no': '1234567890',
            'booking': 1,
            'client': 1
        }

        # Creating instances for testing
        self.client_instance = ClientModel.objects.create(**self.client_data)
        self.booking_instance = BookingModel.objects.create(client=self.client_instance, **self.booking_data)
        self.payment_instance = PaymentModel.objects.create(booking=self.booking_instance, **self.payment_data)
        self.cancel_booking_instance = CancelBookingModel.objects.create(contact_no='1234567890',
                                                                         booking=self.booking_instance,
                                                                         client=self.client_instance)

    def delete_current_model(self, instance):
        instance.delete()

    def client_model_config(self):
        self.assertEqual(self.client_model_instance.name, "Abdul")
        self.assertEqual(self.client_model_instance.email_address, "alvi11225@gmail.com")
        self.assertEqual(self.client_model_instance.phone_no, "+923030709406")

    def client_model_update_config(self):
        self.assertEqual(self.client_model_update_instance.name, "Abdul Rehman")
        self.assertEqual(self.client_model_update_instance.email_address, "alvi11225@gmail.com")
        self.assertEqual(self.client_model_update_instance.phone_no, "+923030709406")

    def booking_model_config(self):
        self.assertEqual(self.booking_model_instance.client, self.client_model_instance)
        self.assertEqual(self.booking_model_instance.booking_date, self.booking_date)
        self.assertEqual(self.booking_model_instance.arrival_time, self.arrival_time)
        self.assertEqual(self.booking_model_instance.end_time, self.end_time)
        self.assertEqual(self.booking_model_instance.payment_status, 'PAID')
        self.assertEqual(self.booking_model_instance.selected_items, self.json_booking_items)
        self.assertEqual(self.booking_model_instance.booking_id, self.booking_id)
        self.assertEqual(self.booking_model_instance.booking_status, 'BOOKED')
        self.assertEqual(self.booking_model_instance.total_price, 50000)
        self.assertEqual(self.booking_model_instance.is_deal, False)

    def booking_model_update_config(self):
        self.assertEqual(self.booking_model_update_instance.client, self.client_model_instance)
        self.assertEqual(self.booking_model_update_instance.booking_date.date(), self.booking_date_update)
        self.assertEqual(self.booking_model_update_instance.arrival_time, self.arrival_time_update)
        self.assertEqual(self.booking_model_update_instance.end_time, self.end_time_update)
        self.assertEqual(self.booking_model_update_instance.payment_status, 'ADVANCE PAID')
        self.assertEqual(self.booking_model_update_instance.selected_items, self.json_booking_items)
        self.assertEqual(self.booking_model_update_instance.booking_id, self.booking_id)
        self.assertEqual(self.booking_model_update_instance.booking_status, 'COMPLETED')
        self.assertEqual(self.booking_model_update_instance.total_price, 500000)
        self.assertEqual(self.booking_model_update_instance.is_deal, False)

    def payment_model_config(self):
        self.assertEqual(self.payment_model_instance.payment_status, 'PAID')
        self.assertEqual(self.payment_model_instance.payment_mode, 'JAZZCASH')
        self.assertEqual(self.payment_model_instance.payment_amount, 5000)
        self.assertEqual(self.payment_model_instance.transaction_id, '123456789012')
        self.assertEqual(self.payment_model_instance.booking, self.booking_model_instance)
        self.assertEqual(self.payment_model_instance.remaining_payment, 45000.0)

    def payment_model_update_config(self):
        self.assertEqual(self.payment_model_update_instance.payment_status, 'ADVANCE PAID')
        self.assertEqual(self.payment_model_update_instance.payment_mode, 'CASH')
        self.assertEqual(self.payment_model_update_instance.payment_amount, 5000)
        self.assertEqual(self.payment_model_update_instance.transaction_id, 123456789000)
        self.assertEqual(self.payment_model_update_instance.booking, self.booking_model_instance)
        self.assertEqual(self.payment_model_update_instance.remaining_payment, 0)

    def cancel_booking_model_config(self):
        self.assertEqual(self.booking_cancel_booking_model.booking, self.booking_model_instance)
        self.assertEqual(self.booking_cancel_booking_model.client, self.client_model_instance)
        self.assertEqual(self.booking_cancel_booking_model.contact_no, "+923030709406")
        self.assertEqual(self.booking_cancel_booking_model.otp, self.booking_cancel_booking_model.otp)

    def cancel_booking_model_update_config(self):
        self.assertEqual(self.booking_cancel_booking_update_model.booking, self.booking_model_instance)
        self.assertEqual(self.booking_cancel_booking_update_model.client, self.client_model_instance)
        self.assertEqual(self.booking_cancel_booking_update_model.contact_no, "+923030709406")
        self.assertEqual(self.booking_cancel_booking_update_model.otp, self.booking_cancel_booking_model.otp)

    def test_booking_client_model_creation(self):
        self.client_model_config()

    def test_booking_client_model_update(self):
        self.client_model_update_config()

    def test_booking_client_model_deletion(self):
        self.client_model_config()

        # Now, delete the instance
        self.delete_current_model(self.client_model_instance)

        # Try to retrieve the instance from the database
        with self.assertRaises(ClientModel.DoesNotExist):
            ClientModel.objects.get(id=self.client_model_instance.id)

    def test_booking_bookings_model_creation(self):
        self.booking_model_config()

    def test_booking_bookings_model_update(self):
        self.booking_model_update_config()

    def test_booking_bookings_model_deletion(self):
        self.booking_model_config()

        # Now, delete the instance
        self.delete_current_model(self.booking_model_instance)

        # Try to retrieve the instance from the database
        with self.assertRaises(BookingModel.DoesNotExist):
            BookingModel.objects.get(id=self.booking_model_instance.id)

    def test_booking_payment_model_creation(self):
        self.payment_model_config()

    def test_booking_payment_model_update(self):
        self.payment_model_update_config()

    def test_booking_payment_model_deletion(self):
        self.payment_model_config()

        # Now, delete the instance
        self.delete_current_model(self.payment_model_instance)

        # Try to retrieve the instance from the database
        with self.assertRaises(PaymentModel.DoesNotExist):
            PaymentModel.objects.get(id=self.client_model_instance.id)

    def test_booking_cancel_booking_creation(self):
        self.cancel_booking_model_config()

    def test_booking_cancel_booking_update(self):
        self.cancel_booking_model_update_config()

    def test_booking_cancel_booking_deletion(self):
        self.cancel_booking_model_config()

        # Now, delete the instance
        self.delete_current_model(self.booking_cancel_booking_model)

        # Try to retrieve the instance from the database
        with self.assertRaises(CancelBookingModel.DoesNotExist):
            CancelBookingModel.objects.get(id=self.client_model_instance.id)

        # Client Serializer Tests

    def test_client_serializer_valid(self):
        serializer = ClientSerializer(instance=self.client_instance)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'name', 'email', 'phone', 'address']))
        self.assertEqual(data['name'], self.client_data['name'])

    def test_client_serializer_invalid(self):
        invalid_data = self.client_data.copy()
        invalid_data['email'] = ''
        serializer = ClientSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Booking Serializer Tests

    def test_booking_serializer_valid(self):
        serializer = BookingSerializer(instance=self.booking_instance)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'client', 'date', 'time', 'service']))
        self.assertEqual(data['service'], self.booking_data['service'])

    def test_booking_serializer_invalid(self):
        invalid_data = self.booking_data.copy()
        invalid_data['date'] = 'invalid-date'
        serializer = BookingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date', serializer.errors)

        # Payment Serializer Tests

    def test_payment_serializer_valid(self):
        serializer = PaymentSerializer(instance=self.payment_instance)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['id', 'booking', 'amount', 'payment_date', 'payment_method']))
        self.assertEqual(data['amount'], self.payment_data['amount'])

    def test_payment_serializer_invalid(self):
        invalid_data = self.payment_data.copy()
        invalid_data['amount'] = 'invalid-amount'
        serializer = PaymentSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)

        # Cancel Booking Serializer Tests

    def test_cancel_booking_serializer_valid(self):
        serializer = CancelBookingSerializer(instance=self.cancel_booking_instance)
        data = serializer.data
        self.assertEqual(set(data.keys()), set(['contact_number', 'booking', 'client']))
        self.assertEqual(data['contact_number'], self.cancel_booking_instance.contact_no)

    def test_cancel_booking_serializer_invalid(self):
        invalid_data = self.cancel_booking_data.copy()
        invalid_data['contact_no'] = ''
        serializer = CancelBookingSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('contact_number', serializer.errors)

    def test_cancel_booking_serializer_contact_number_mapping(self):
        serializer = CancelBookingSerializer(instance=self.cancel_booking_instance)
        data = serializer.data
        self.assertEqual(data['contact_number'], '1234567890')

        # Create object using serializers

    def test_create_client(self):
        serializer = ClientSerializer(data=self.client_data)
        self.assertTrue(serializer.is_valid())
        client = serializer.save()
        self.assertEqual(client.name, self.client_data['name'])

    def test_create_booking(self):
        serializer = BookingSerializer(data=self.booking_data)
        self.assertTrue(serializer.is_valid())
        booking = serializer.save()
        self.assertEqual(booking.service, self.booking_data['service'])

    def test_create_payment(self):
        serializer = PaymentSerializer(data=self.payment_data)
        self.assertTrue(serializer.is_valid())
        payment = serializer.save()
        self.assertEqual(payment.amount, self.payment_data['amount'])

    def test_create_cancel_booking(self):
        serializer = CancelBookingSerializer(data=self.cancel_booking_data)
        self.assertTrue(serializer.is_valid())
        cancel_booking = serializer.save()
        self.assertEqual(cancel_booking.contact_no, self.cancel_booking_data['contact_no'])
