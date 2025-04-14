from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User



class BaseStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(class)s_created_by')
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


class EmailTemplate(BaseStampedModel):
    templates = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=255, default='subject')
    body = RichTextField(default='body')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="template_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="template_updated"
                                   )

    def __str__(self):
        return self.templates

    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'

    def save(self, *args, **kwargs):
        from booking.models import check_admin_call
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)