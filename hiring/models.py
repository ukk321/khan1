from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from booking.models import check_admin_call

# Define the "system" user


def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("The maximum file size that can be uploaded is 5 MB.")


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


class DesignationModel(BaseStampedModel):
    job_title = models.CharField(max_length=200, null=False, blank=False, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="designation_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="designation_updated")

    def __str__(self):
        return self.job_title

    class Meta:
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class HiringModel(BaseStampedModel):
    name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(max_length=200, null=True, blank=True)
    upload_cv = models.FileField(upload_to='images/', null=True, blank=True,
                                 validators=[FileExtensionValidator(allowed_extensions=["pdf", 'docx', 'doc']),
                                             validate_file_size])
    message = models.TextField(max_length=200, null=True, blank=False)
    position_applying_for = models.ForeignKey(DesignationModel, on_delete=models.CASCADE, null=True, blank=False,
                                              related_name="hiring")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="hiring_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="hiring_updated")
    is_approved = models.BooleanField(default=False, null=True, blank=True)
    phone_number = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Hiring'
        verbose_name_plural = 'Hirings'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)

    def save_and_approve(self, *args, **kwargs):
        # This method can be used to both save and approve the hiring
        self.is_approved = True
        self.save(*args, **kwargs)


@receiver(post_save, sender=HiringModel)
def update_our_team(instance,**kwargs):
    try:
        our_team_member = OurTeamModel.objects.get(
            name=instance.name,
            designation=instance.position_applying_for.job_title
        )
        if instance.is_approved:
            our_team_member.is_active = True
        else:
            our_team_member.delete()
    except OurTeamModel.DoesNotExist:
        if instance.is_approved:
            OurTeamModel.objects.create(
                name=instance.name,
                designation=instance.position_applying_for.job_title,
                is_active=False,
                created_by=instance.created_by,
                updated_by=instance.updated_by if instance.updated_by and instance.updated_by.is_staff else None
            )


class OurTeamModel(BaseStampedModel):
    name = models.CharField(max_length=25, null=True, blank=False)
    designation = models.CharField(max_length=30, null=True, blank=False)
    image = models.FileField(upload_to='images/', null=True, blank=True,
                             validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])])
    is_active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_updated")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Our Team'
        verbose_name_plural = 'Our Team'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)
