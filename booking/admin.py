import logging

from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse, path
from django.utils.html import format_html
from jaraco.text import _
from booking.models import ClientModel, BookingModel, PaymentModel, CancelBookingModel
from utils.email_service import EmailService
from booking.widgets import HierarchicalNamesJSONWidget

logger = logging.getLogger(__name__)


def disable_fields(form,obj=None):
    # Disable related fields controls
    form.base_fields['created_by'].widget.can_change_related = False
    form.base_fields['created_by'].widget.can_add_related = False
    form.base_fields['created_by'].widget.can_view_related = False
    form.base_fields['created_by'].widget.can_delete_related = False
    form.base_fields['updated_by'].widget.can_change_related = False
    form.base_fields['updated_by'].widget.can_add_related = False
    form.base_fields['updated_by'].widget.can_view_related = False
    form.base_fields['updated_by'].widget.can_delete_related = False

    # Disable the fields when editing existing clients
    if obj:
        form.base_fields['created_by'].disabled = True
        form.base_fields['updated_by'].disabled = True

    return form


class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email_address', 'phone_no','city']
    list_per_page = 10
    list_filter = ['name', 'email_address', 'phone_no']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Disable the 'add' action
    def has_add_permission(self, request, obj=None):
        return False

    # Enable the 'change' action
    def has_change_permission(self, request, obj=None):
        return True

    # Enable the 'view' action
    def has_view_permission(self, request, obj=None):
        return True

    # Disable deletion of records
    def has_delete_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user

        # Set updated_by field for new and existing objects
        obj.updated_by = request.user

        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = BookingModel
        fields = '__all__'
        widgets = {
            'selected_items': HierarchicalNamesJSONWidget(attrs={'rows': 10, 'cols': 80}),
        }


def get_selected_items_details(selected_items):
    services = selected_items.get('services', [])
    deals = selected_items.get('deals', [])
    all_names = []
    total_persons = 0
    total_price = 0
    has_deals = False

    def extract_service_details(item_list, all_names):
        nonlocal total_persons
        for item in item_list:
            name = item.get('name', 'Unnamed')
            all_names.append(name)
            total_persons += item.get('no_of_persons', 0)
            if 'categories' in item:
                extract_service_details(item.get('categories', []), all_names)
            if 'sub_services' in item:
                extract_service_details(item.get('sub_services', []), all_names)
            if 'subservice_category' in item:
                extract_service_details(item.get('subservice_category', []), all_names)

    def extract_deal_details(item_list, all_names):
        nonlocal total_persons, total_price
        for item in item_list:
            name = item.get('name', 'Unnamed')
            all_names.append(name)
            total_persons += item.get('numPersons', 0)
            total_price += item.get('discounted_price', 0)

    if services:
        extract_service_details(services, all_names)
    if deals:
        has_deals = True
        extract_deal_details(deals, all_names)

    return all_names, total_persons, total_price, has_deals


@admin.register(BookingModel)
class BookingAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'
    form = BookingAdminForm
    list_display = ['client', 'order_date', 'dispatch_date', 'order_id',
                    'order_status', 'total_price','is_gift', 'cancel_appointment']
    list_per_page = 10
    search_fields = ['order_id', 'order_date']
    list_filter = ['client__name','is_gift']

    def cancel_appointment(self, obj):
        if obj.order_status.lower() == 'completed' and obj.order_status.lower() == 'cancelled' or CancelBookingModel.objects.filter(
                booking=obj).exists():
            return format_html(
                '<a class="button" style="background-color:grey;color:white;padding:5px 10px;'
                'border-radius:5px;cursor:not-allowed;" disabled>Cancelled</a>'
            )
        else:
            return format_html(
                '<a class="button" style="background-color:red;color:white;padding:5px 10px;'
                'border-radius:5px;text-decoration:none;display:inline-block;'
                '" href="{}" onclick="return confirm(\'Are you sure you want to cancel the booking?\');">Cancel</a>',
                reverse('admin:cancel-booking', args=[obj.pk])
            )

    cancel_appointment.short_description = 'Cancel Order'
    cancel_appointment.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cancel-booking/<int:booking_id>/', self.admin_site.admin_view(self.process_cancellation),
                 name='cancel-booking'),
        ]
        return custom_urls + urls

    def process_cancellation(self, request, booking_id):
        booking = self.get_object(request, booking_id)
        if booking:
            cancel_booking = CancelBookingModel(
                booking=booking,
                client=booking.client,
                contact_no=booking.client.phone_no,
                created_by=request.user,
                updated_by=request.user,
            )
            cancel_booking.save()

            booking.booking_status = 'CANCELLED'
            booking.save()

            client_email = booking.client.email_address
            selected_items_names, total_persons, total_price, has_deals = get_selected_items_details(
                booking.selected_items)
            booking_details = {
                'client_name': booking.client.name,
                'shipment_id': booking.booking_id,
                'order_date': booking.booking_date,
                'arrival_time': booking.arrival_time,
                'end_time': booking.end_time,
                'contact_no': booking.client.phone_no,
                'total_price': booking.total_price,
                'selected_items': ', '.join(selected_items_names),
                'booking_status': 'Cancelled',
                'cancellation_message': "Cancelled by Admin"
            }

            EmailService.send_email_with_template_key(
                template_key='Shipment_Cancellation',
                recipients=[client_email],
                context=booking_details
            )
            self.message_user(request, f"Booking {booking.booking_id} has been cancelled.")
        return redirect(reverse('admin:booking_cancelbookingmodel_changelist'))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)

        if obj.order_date and obj.dispatch_date:
            try:
                client_email = obj.client.email_address
                selected_items_names, total_persons, total_price, has_deals = get_selected_items_details(
                    obj.selected_items)

                payment_instance, created = PaymentModel.objects.get_or_create(
                    booking=obj,
                    defaults={
                        'payment_status': 'PENDING',
                        'payment_amount': total_price if has_deals else obj.total_price,
                        'created_by': request.user,
                        'updated_by': request.user,
                    }
                )

                if not created:
                    payment_instance.payment_status = 'PENDING'
                    payment_instance.payment_amount = total_price if has_deals else obj.total_price
                    payment_instance.updated_by = request.user
                    payment_instance.save()

                booking_details = {
                    'client_name': obj.client.name,
                    'order_date': obj.booking_date,
                    'shipment_id': obj.booking_id,
                    'arrival_time': obj.arrival_time,
                    'end_time': obj.end_time,
                    'selected_items': ', '.join(selected_items_names),
                    'total_price': total_price if has_deals else obj.total_price,
                    'contact_no': obj.client.phone_no,
                    'no_of_persons': total_persons,
                    'payment_status': obj.payment_status
                }

                EmailService.send_email_with_template_key(
                    template_key='Booking_Time_Allocation',
                    recipients=[client_email],
                    context=booking_details
                )
                logger.info(f'Email Notification sent to {client_email}')
            except Exception as e:
                logger.error(f'Error occurred while sending email notification: {e}')

    def booking_status_colored(self, obj):
        color = 'red' if obj.booking_status.lower() == 'cancelled' else 'black'
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.booking_status,
        )

    booking_status_colored.short_description = 'Booking Status'


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'
    list_display = ['payment_amount', 'payment_method', 'order',
                    'transaction_id']
    list_per_page = 10
    from booking.forms import PaymentModelForm
    form = PaymentModelForm
    list_filter = ['payment_method', 'payment_amount', 'order']
    fields = (
        'payment_amount', 'payment_method', 'order', 'transaction_id', 'created_by',
        'updated_by')
    readonly_fields = ('transaction_id', 'payment_amount')
    search_fields = ['created_at', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class CancelBookingAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'
    list_display = ['client', 'booking_link', 'contact_no', 'otp']
    list_per_page = 10
    search_fields = ['created_at', ]

    def booking_link(self, obj):
        # Generate the URL for the change view of the related BookingModel
        if obj.booking:
            url = reverse('admin:booking_bookingmodel_change', args=[obj.booking.pk])
            return format_html('<a href="{}">{}</a>', url, obj.booking.order_id)
        return _('No Booking')

    booking_link.short_description = 'Order'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


admin.site.register(CancelBookingModel, CancelBookingAdmin)
admin.site.register(ClientModel, ClientAdmin)
