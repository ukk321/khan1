from django.contrib import admin
from django.core.paginator import Paginator
from django.urls import path
from booking.admin import disable_fields
from policies.models import PolicyModel, DealModel
from policies.views import create_deal
from services.models import ServiceModel


class PolicyAdmin(admin.ModelAdmin):
    list_display = ['title','is_active']
    list_filter = ['is_active']
    search_fields = ['title']
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


class DealAdmin(admin.ModelAdmin):
    change_list_template = 'custom_deal_template/change_list.html'
    list_display = ['name', 'price']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('create_deal/', self.admin_site.admin_view(create_deal), name='create_deal'),
        ]
        return custom_urls + urls

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        paginator = Paginator(queryset, 10)  # Show 10 items per page
        page_number = request.GET.get('p')
        page_obj = paginator.get_page(page_number)
        extra_context['result_list'] = page_obj
        extra_context['cl'] = self
        extra_context['paginator'] = paginator
        extra_context['page_obj'] = page_obj
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        # Check if the request is for changing the deal model view
        if request.resolver_match.view_name == 'admin:policies_dealmodel_change':
            return super().get_queryset(request)
        else:
            return ServiceModel.objects.prefetch_related('categories__category_service').all()

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(PolicyModel,PolicyAdmin)
admin.site.register(DealModel,DealAdmin)