from django.contrib import admin
from django.utils.html import format_html
from booking.admin import disable_fields
from hiring.models import HiringModel, DesignationModel, OurTeamModel


class DesignationAdmin(admin.ModelAdmin):
    list_display = ['job_title']
    search_fields = ['job_title']
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


@admin.register(HiringModel)
class HiringAdmin(admin.ModelAdmin):
    list_display = ['name','email','upload_cv_link','message','position_applying_for','is_approved']
    search_fields = ['name']
    list_filter = ['position_applying_for','is_approved']
    list_per_page = 10

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return disable_fields(form,obj)

    def upload_cv_link(self, obj):
        pdf_url = obj.upload_cv.url if obj.upload_cv else None
        if pdf_url:
            return format_html('<a href="{}" target="_blank">View PDF</a>', pdf_url)
        else:
            return '-'

    upload_cv_link.short_description = 'Upload CV'

    def save_model(self, request, obj, form, change):
        # Set created_by field for new objects
        if not change:
            obj.created_by = request.user
        # Set updated_by field for new and existing objects
        obj.updated_by = request.user
        # Call the super method to save the object
        super().save_model(request, obj, form, change)


class OurTeamAdmin(admin.ModelAdmin):
    list_display = ['name','designation','image','is_active']
    list_filter = ['is_active']
    search_fields = ['designation']
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


admin.site.register(DesignationModel,DesignationAdmin)
admin.site.register(OurTeamModel,OurTeamAdmin)