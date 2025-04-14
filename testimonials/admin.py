from django.contrib import admin
from django.utils.html import format_html
from booking.admin import disable_fields
from testimonials.models import TestimonialModel, SocialHandleModel


class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name','email','location','truncated_message','file_type','isApproved']
    list_filter = ['isApproved']
    search_fields = ['name']
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

    def truncated_message(self, obj):
        # Define the maximum number of words to display
        max_words = 8  # Adjust the number according to your preference

        # Get the full message
        message = obj.message

        # Split the message into words
        words = message.split()

        # Check if the number of words exceeds the maximum
        if len(words) > max_words:
            # Truncate the message to the desired number of words and append ellipsis
            truncated_message = ' '.join(words[:max_words]) + '...'
        else:
            # If within the limit, return the full message
            truncated_message = message

        return format_html('<div style="width: 250px; overflow: hidden;">{}</div>', truncated_message)

    # Customize the display name of the truncated message column
    truncated_message.short_description = 'Message'

    def file_type(self, obj):
        """ Return either 'Image' or 'Video' depending on the file type, or 'No file' if no file is provided. """
        if obj.file:
            file_name = obj.file.name.lower()
            if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return 'Image'
            elif file_name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                return 'Video'
        return ''

    file_type.short_description = 'File'


class SocialHandleAdmin(admin.ModelAdmin):
    list_display = ['name','url','is_active','icon','icon_code']
    search_fields = ['name']
    list_filter = ['is_active']
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


admin.site.register(TestimonialModel,TestimonialAdmin)
admin.site.register(SocialHandleModel,SocialHandleAdmin)