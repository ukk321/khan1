import logging
import random
import string

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils.email_service import EmailService

logger = logging.getLogger(__name__)


def check_admin_call(kwargs):
    if 'request' in kwargs and kwargs['request'].user.is_staff:
        # Call is from admin panel
        return kwargs['request'].user
    else:
        # Call is from frontend
        system_user, created = User.objects.get_or_create(username='system')
        return system_user


class BaseStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(class)s_created_by', default="'%(class)s_created_by")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(class)s_updated_by')

    class Meta:
        abstract = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['created_by'].disabled = True
            form.base_fields['updated_by'].disabled = True
        return form

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.updated_by = None
        super().save(*args, **kwargs)


class ClientModel(BaseStampedModel):
    name = models.CharField(max_length=200, null=False, blank=False, default='Name')
    email_address = models.EmailField(max_length=200, null=False, blank=False, default='Email')
    address=models.TextField()
    phone_regex = RegexValidator(
        regex=r'^\+(?:[0-9] ?){6,14}[0-9]$',
        message="Phone number must be entered in the format: '+999999999'. Country code required."
    )
    phone_no = models.CharField(max_length=20, validators=[phone_regex], null=False, blank=False, default='Phone')
    city=models.CharField(max_length=100,blank=False)
    postal_code=models.CharField(max_length=20,blank=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def save(self, *args, **kwargs):

        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


def generate_unique_order_id(length=10):
    prefix = "EShp#"
    characters = string.digits
    random_part = ''.join(random.choices(characters, k=length))
    return f'{prefix}{random_part}'


class BookingModel(BaseStampedModel):
    SHIPPING_METHODS = [
      ('standard','Standard Shipping')   
       ]
    ORDER_STATUS = [
        ('BOOKED', 'Booked'),
        ('IN_PROGRESS', 'In Progress'),
        ('DISPATCHED','Dispatched'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    client = models.ForeignKey(ClientModel, on_delete=models.CASCADE, blank=True, null=False)
    order_date = models.DateTimeField(auto_now_add=False, null=True)
    dispatch_date = models.TimeField(null=True, blank=True)
    
    shipping_method=models.CharField(choices=SHIPPING_METHODS,max_length=20,default='standard')
    selected_items = models.JSONField(max_length=1000, null=True, blank=True)
    order_id = models.CharField(max_length=20, unique=False, default=generate_unique_order_id, editable=False)
    
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, default='BOOKED')
    total_price = models.IntegerField(null=True, blank=False)
    is_gift = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="booking_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="booking_updated"
                                   )

    def __str__(self):
        formatted_date = self.order_date.strftime("%d-%m-%Y %H:%M")

        if self.selected_items:
            if self.is_gift:
                deal_names = ', '.join([item.get('name') for item in self.selected_items.get('deals', [])])
                selected_items_str = f"Deals: {deal_names}"
            else:
                service_names = ', '.join([item.get('name') for item in self.selected_items.get('services', [])])
                selected_items_str = f"Services: {service_names}"
        else:
            selected_items_str = "No items selected"

        return f"{self.order_id} | {self.client.name} | {selected_items_str} | {formatted_date}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        is_new = not self.pk
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        try:
            old_booking = BookingModel.objects.get(pk=self.pk)
            old_payment_status = old_booking.payment_status
        except BookingModel.DoesNotExist:
            old_payment_status = None

        if not is_new and not self.selected_items:
            old_booking = BookingModel.objects.get(pk=self.pk)
            self.selected_items = old_booking.selected_items

        if self.selected_items is None:
            self.selected_items = {}

        self.is_deal = 'deals' in self.selected_items and bool(self.selected_items.get('deals'))

        super().save(*args, **kwargs)

        # if not is_new:
        #     for payment in self.payments.all():
        #         payment.payment_amount = self.total_price
        #         payment.save()

        # # Check if payment_status changed to PAID
        # if old_payment_status != 'PAID' and self.payment_status == 'PAID' and self.client and self.client.email_address:
        #     try:
        #         client_email = self.client.email_address

        #         logger.info(f"Email notification sent to {client_email}")
        #     except Exception as e:
        #         logger.error(f"Error occurred while sending email notification: {e}")


class PaymentModel(BaseStampedModel):
    PAYMENT_METHODS=[
        ('card','Debit/Credit Card'),
        ('cod','Cash On Delivery'),
    ]

    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cod')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, editable=False)
    transaction_id = models.BigIntegerField(null=True, blank=False)
    order = models.ForeignKey('BookingModel', on_delete=models.CASCADE, related_name='payments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="payment_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="payment_updated"
                                   )

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def save(self, *args, **kwargs):
        is_new = not self.pk
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        try:
            old_payment = PaymentModel.objects.get(pk=self.pk)
            old_payment_status = old_payment.payment_status
        except PaymentModel.DoesNotExist:
            old_payment_status = None

        if is_new:
            self.payment_amount = self.booking.total_price * 0.1
            self.remaining_payment = self.booking.total_price - self.payment_amount

        if not is_new:
            self.payment_amount = self.payment_amount + self.remaining_payment
            self.remaining_payment = self.booking.total_price - self.payment_amount
        super().save(*args, **kwargs)

        # Check if payment_status changed to PAID
        if old_payment_status != 'PAID' and self.payment_status == 'PAID' and self.booking_id:
            try:
                # Retrieve the related booking
                related_booking = self.booking
                if related_booking.client and related_booking.client.email_address:
                    client_email = related_booking.client.email_address
                    from booking.admin import get_selected_items_details
                    selected_items_names, total_persons, total_price, has_deals = get_selected_items_details(
                        related_booking.selected_items)
                    booking_details = {
                        'client_name': related_booking.client.name,
                        'shipment_id': related_booking.booking_id,
                        'payment_status': self.payment_status,
                        'selected_items': ', '.join(selected_items_names),
                        'no_of_persons': total_persons,
                        'booking_date': related_booking.booking_date,
                        'arrival_time': related_booking.arrival_time,
                        'total_price': total_price if has_deals else related_booking.total_price
                    }

                    EmailService.send_email_with_template_key(template_key='Booking_Confirmation',
                    recipients=[client_email],
                    context=booking_details)

                    logger.info(f"Email notification sent to {client_email}")
            except Exception as e:
                logger.error(f"Error occurred while sending email notification: {e}")


@receiver(post_save, sender=BookingModel)
def update_payment_status_on_booking_save(instance,**kwargs):
    try:
        payment_instance = instance.payments.first()
        if payment_instance:
            if payment_instance.payment_status != instance.payment_status:
                payment_instance.payment_status = instance.payment_status
                payment_instance.save()
    except PaymentModel.DoesNotExist:
        pass


@receiver(post_save, sender=PaymentModel)
def update_payment_status_on_payment_save(instance,**kwargs):
    try:
        booking_instance = instance.booking
        if booking_instance.payment_status != instance.payment_status:
            booking_instance.payment_status = instance.payment_status
            booking_instance.save()
    except BookingModel.DoesNotExist:
        pass


def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choices(characters, k=length))
    return otp


class CancelBookingModel(BaseStampedModel):
    booking = models.ForeignKey('BookingModel', on_delete=models.CASCADE, related_name='cancel_appointment', null=True)
    client = models.ForeignKey(ClientModel, on_delete=models.CASCADE, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+(?:[0-9] ?){6,14}[0-9]$',
        message="Phone number must be entered in the format: '+999999999'. Country code required."
    )
    contact_no = models.CharField(max_length=20, validators=[phone_regex], null=False, blank=False, default='Phone')
    otp = models.CharField(max_length=6, default=generate_otp, editable=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="cancelbooking_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="cancelbooking_updated")

    class Meta:
        verbose_name = 'Cancel Shipment'
        verbose_name_plural = 'Cancel Shipments'

    def __str__(self):
        return f"Cancel Booking | {self.client.name} | {self.contact_no}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp = generate_otp()

        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)