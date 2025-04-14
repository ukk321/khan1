from rest_framework import serializers

from booking.models import ClientModel, BookingModel, PaymentModel, CancelBookingModel


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientModel
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingModel
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = '__all__'


class CancelBookingSerializer(serializers.ModelSerializer):
    contact_number = serializers.CharField(source='contact_no')

    class Meta:
        model = CancelBookingModel
        fields = ["contact_number", "booking", "client"]
