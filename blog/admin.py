from .models import Blog,Tag,NewsletterSubscriber
from . import models
from booking.admin import disable_fields
from ckeditor.widgets import CKEditorWidget
from django.contrib import admin, messages
from utils.email_service import EmailService
from django.template import Template, Context

# Register your models here.
class TagAdmin(admin.ModelAdmin):
    list_display=['id','name']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class BlogAdmin(admin.ModelAdmin):
    list_display=('title','author','isNewsletter')
    formfield_overrides = {
        models.RichTextField: {'widget': CKEditorWidget},
    }
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for blog in queryset:
            if not blog.isNewsletter:
                self.message_user(request, f"Blog '{blog.title}' is not marked as a newsletter.", messages.WARNING)
                continue

            subscribers = NewsletterSubscriber.objects.values_list('email', flat=True)
            if subscribers:
                try:
                    context={'content':blog.content}
                    template = Template(blog.content)
                    rendered_body = template.render(Context(context))
                    EmailService.send_email_with_template_key(
                        template_key='Newsletter_Mail',
                        recipients=subscribers,
                        context={'content':rendered_body})
                    self.message_user(request, f"Newsletter '{blog.title}' sent to subscribers.", messages.SUCCESS)
                except Exception as e:
                    self.message_user(request, f"Error sending newsletter '{blog.title}': {e}", messages.ERROR)
            else:
                self.message_user(request, "No subscribers found.", messages.WARNING)

    send_newsletter.short_description = "Send selected blog(s) as newsletter"


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display=['email']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['created_by', 'updated_by']:
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        return disable_fields(form,obj)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Tag,TagAdmin)
admin.site.register(Blog,BlogAdmin)
admin.site.register(NewsletterSubscriber,NewsletterSubscriberAdmin)