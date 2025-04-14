from django.contrib import admin
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html
from booking.admin import disable_fields
from lacigal import settings
from .forms import SubServicesAdminForm
from .models import ServiceModel, SubServicesModel,ProductSizeAttribute, CategoryModel,ContactUs, Reply,ProductsImage,AttributeNameModel,AttributeValueModel,ProductAttribute
from utils.email_service import EmailService
from django import forms
from .models import Size, SizeCategory, SizeAttribute
# Register your models here.

class ProductSizeAttributeInline(admin.TabularInline):
    model = ProductSizeAttribute
    extra = 1
    fields = ['size_attribute']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

class BranchAdmin(admin.ModelAdmin):
    list_display = ['name','address','branch_contact','branch_owner','owner_contact']
    search_fields = ['name','address','branch_contact','branch_owner','owner_contact']
    list_per_page = 10

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


@admin.register(AttributeNameModel)
class AttributeNameAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_per_page=10
    search_fields=['name']

    def formfield_for_foreignkey(self,db_field,request,**kwargs):
        if db_field.name in ['created_by','updated_by']:
            kwargs['disabled']=True
        return super().formfield_for_foreignkey(db_field,request,**kwargs)
    
    def get_form(self,request,obj=None,**kwargs):
        form=super().get_form(request,obj,**kwargs)

        return disable_fields(form,obj)

    def save_model(self,request,obj,form,change):
        if not change:
            obj.created_by=request.user
        obj.updated_by=request.user
        super().save_model(request,obj,form,change)


@admin.register(AttributeValueModel)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute_name','value']
    list_per_page=10
    search_fields=['attribute_name__name','value']

    def formfield_for_foreignkey(self,db_field,request,**kwargs):
        if db_field.name in ['created_by','updated_by']:
            kwargs['disabled']=True
        return super().formfield_for_foreignkey(db_field,request,**kwargs)
    
    def get_form(self,request,obj=None,**kwargs):
        form=super().get_form(request,obj,**kwargs)

        return disable_fields(form,obj)

    def save_model(self,request,obj,form,change):
        if not change:
            obj.created_by=request.user
        obj.updated_by=request.user
        super().save_model(request,obj,form,change)

class ProductAttributeInlineForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['attribute_value', 'quantity']
        widgets = {
            'attribute_value': forms.SelectMultiple(attrs={'class': 'admin-multiselect'})
        }

class ProductAttributeInline(admin.TabularInline):
    model=ProductAttribute
    extra=1
    form=ProductAttributeInlineForm
    fields=['attribute_value','quantity']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form, obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)



class ServiceAdmin(admin.ModelAdmin):
    change_list_template = 'custom_hierarchical_services/change_list.html'
    list_display = ['name', 'heading', 'description', 'price_range', 'image']
    search_fields = ['name', 'heading', 'description']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form, obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            cl = response.context_data['cl']
            paginator = Paginator(cl.result_list, self.list_per_page)
            page_number = request.GET.get('p', 1)
            page_obj = paginator.get_page(page_number)
            response.context_data['cl'] = cl
            response.context_data['page_obj'] = page_obj  # Pass the page object to the context
        except (KeyError, AttributeError):
            pass
        return response

    def get_queryset(self, request):
        return ServiceModel.objects.prefetch_related('categories__category_service').all().order_by('created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','service','description']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form, obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class ProductImageAdmin(admin.StackedInline):
    model=ProductsImage


class SubServiceAdmin(admin.ModelAdmin):
    inlines=[ProductImageAdmin,ProductAttributeInline,ProductSizeAttributeInline]
    form = SubServicesAdminForm
    list_display = ['name', 'heading', 'truncated_description', 'price', 'discounted_price', 'image', 'service', 'category', 'subservice','size_chart_button']
    list_filter = ['category__name', 'service__name']
    search_fields = ['name', 'heading', 'description']
    list_per_page = 10

    def size_chart_button(self, obj):

        return format_html(

        '<a class="button" href="{}" target="_blank">View Size Chart</a>',

        reverse('admin:view_size_chart', args=[obj.pk])

        )

    size_chart_button.short_description = "Size Chart"

  

    def get_urls(self):

        from django.urls import path

        urls = super().get_urls()

        custom_urls = [

        path('<int:subservice_id>/', self.view_size_chart, name='view_size_chart'),

        ]

        return custom_urls + urls

  

  # Render the size chart page

    def view_size_chart(self, request, subservice_id):

        # Fetch product data from the API

        try:

            from django.http import Http404

            import requests

            response = requests.get(f"https://ecommbe.psykick.ae/collection/products/?id={subservice_id}")

            response.raise_for_status()

            product_data = response.json()

        except requests.RequestException:

            raise Http404("Product data could not be fetched.")

    

        # Extract sizes data if available

        sizes = product_data.get("Products", [{}])[0].get("sizes", [])

    

        # Render the size chart template with product data and sizes

        return render(request, 'admin/size_chart.html', {

        'subservice': product_data,

        'sizes': sizes

        })


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form, obj)

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)

    def truncated_description(self, obj):
        max_length = 50

        description = obj.description or ''

        if len(description) > max_length:
            truncated_description = description[:max_length] + '...'
        else:
            truncated_description = description

        return format_html('<div style="width: 250px; overflow: hidden;">{}</div>', truncated_description)

    truncated_description.short_description = 'Description'


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'message', 'get_image', 'reply_button', 'created_at')
    search_fields = ['name','message']
    list_per_page = 10

    def get_image(self, obj):
        if obj.choose_file:
            return format_html('<img src="{}" style="max-height:100px; max-width:100px;">', obj.choose_file.url)

    def reply_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Reply</a>',
            reverse('admin:reply_to_contact', args=[obj.pk])
        )
    reply_button.short_description = "Reply"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('reply/<int:contact_id>/', self.reply_to_contact, name='reply_to_contact'),
        ]
        return custom_urls + urls

    def reply_to_contact(self, request, contact_id):
        if request.user.is_authenticated:
            contact = ContactUs.objects.get(pk=contact_id)
            previous_replies = Reply.objects.filter(contact=contact)

            if request.method == 'POST':
                reply_message = request.POST.get('reply_message')
                Reply.objects.create(contact=contact, message=reply_message)
                EmailService.send_email_with_template_key(template_key='Reply_User',recipients=[contact.email],context={'name': contact.name, 'message': reply_message})

                self.message_user(request, "Your reply has been saved and sent successfully.")
                return HttpResponseRedirect(reverse('admin:services_contactus_changelist'))
            else:
                return render(request, 'reply.html', {'contact': contact, 'previous_replies': previous_replies})
        else:
            admin_reply_link = settings.EMAIL_REPLY_URL.format(contact_id)

            next_url = reverse('admin:login') + f'?next={admin_reply_link}'
            return redirect(next_url)

    def has_add_permission(self, request, obj=None):
        return False


class SizeAttributeInline(admin.TabularInline):
    model = SizeAttribute
    extra = 1
    fields = ('attribute_name', 'value_in_cm', 'value_in_inches')
    readonly_fields = ('value_in_inches',)

    def value_in_inches(self, obj):
        return obj.get_value(unit='inches')
    
    value_in_inches.short_description = 'Value (inches)'

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size', 'category')
    list_filter = ('category',)
    search_fields = ('size', 'category__name')
    inlines = [SizeAttributeInline]


@admin.register(SizeCategory)
class SizeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SizeAttribute)
class SizeAttributeAdmin(admin.ModelAdmin):
    list_display = ('size', 'attribute_name', 'value_in_cm', 'value_in_inches')
    list_filter = ('size__category',)
    search_fields = ('size__size', 'attribute_name')

    def value_in_inches(self, obj):
        return obj.get_value(unit='inches')

    value_in_inches.short_description = 'Value (inches)'


admin.site.register(ServiceModel, ServiceAdmin)
admin.site.register(CategoryModel, CategoryAdmin)
admin.site.register(SubServicesModel, SubServiceAdmin)
admin.site.register(ContactUs, ContactUsAdmin)

