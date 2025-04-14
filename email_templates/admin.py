from django.contrib import admin
from .models import EmailTemplate
from booking.admin import disable_fields

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):

    list_display = ('templates', 'subject')
    list_per_page = 10

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            readonly_fields += ('templates',)  # Make templates field readonly for existing objects
        return readonly_fields

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

