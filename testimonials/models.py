from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from booking.models import check_admin_call

from testimonials.utils import FeedbackNotification


def validate_image_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("The maximum file size for images is 5 MB.")


def validate_video_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("The maximum file size for videos is 10 MB.")


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


class TestimonialModel(BaseStampedModel):
    name = models.CharField(max_length=200, null=False, blank=False,)
    email = models.EmailField(max_length=200, null=True, blank=True)
    location=models.CharField(max_length=250,null=True,blank=True)
    message = models.TextField(null=False, blank=False)
    file = models.FileField(upload_to='images/', null=True, blank=True,
                            validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi","mkv"])])
    isApproved = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="testimonial_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="testimonial_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        is_new_instance = self.pk is None  # Check if this is a new instance
        previous_is_approved = None

        # If it's an existing instance, retrieve the previous value of isApproved
        if not is_new_instance:
            previous_instance = TestimonialModel.objects.get(pk=self.pk)
            previous_is_approved = previous_instance.isApproved

        super().save(*args, **kwargs)

        if self.isApproved and (is_new_instance or previous_is_approved is False):
            # Prepare the feedback details
            feedback_details = {
                'name': self.name,
                'email': self.email,
                'message': self.message,
                'location': self.location,
            }

            FeedbackNotification.send_approval_mail_to_user(self.email, feedback_details)

    def truncated_message(self, length=100):
        """ Return a truncated version of the message with ellipsis if necessary. """
        if len(self.message) > length:
            return self.message[:length] + '...'
        return self.message

    def clean(self):
        file = self.file
        if file:
            if file.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                validate_image_size(file)
            elif file.name.endswith(('.mp4', '.mov', '.avi','.mkv')):
                validate_video_size(file)


class SocialHandleModel(BaseStampedModel):
    name=models.CharField(max_length=50,null=True,blank=True)
    url=models.CharField(max_length=100,null=True,blank=True)
    is_active=models.BooleanField(default=False,null=True,blank=True)
    icon = models.ImageField(upload_to='images/', null=True, blank=True)
    icon_code = models.CharField(max_length=100, null=True, blank=True)
    svg_code = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="account_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="account_updated")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'SocialHandle'
        verbose_name_plural = 'SocialHandles'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)

    def save_and_approve(self, *args, **kwargs):
        self.is_approved = True
        self.save(*args, **kwargs)
