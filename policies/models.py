from ckeditor.fields import RichTextField
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from booking.models import check_admin_call
from services.models import ServiceModel, CategoryModel, SubServicesModel


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


class PolicyModel(BaseStampedModel):
    title = models.CharField(max_length=100)
    content = RichTextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="policy_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="policy_updated")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Policy'
        verbose_name_plural = 'Policies'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class DealModel(BaseStampedModel):
    name=models.CharField(max_length=200,null=True,blank=False,unique=True)
    service_title=models.ManyToManyField(ServiceModel, blank=True,null=False, related_name="deals")
    category=models.ManyToManyField(CategoryModel, blank=True,null=False, related_name="deals")
    subservice=models.ManyToManyField(SubServicesModel, blank=True,null=False, related_name="deals")
    price = models.IntegerField(default=0,null=True, blank=False)
    discounted_price = models.IntegerField(default=0, null=True, blank=True)
    is_active=models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="deal_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="deal_updated")

    def __str__(self):
       return self.name

    class Meta:
        verbose_name='Deal'
        verbose_name_plural='Deals'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


@receiver(m2m_changed, sender=DealModel.subservice.through)
def update_discounted_price(instance,**kwargs):
    total_price = sum(subservice.price for subservice in instance.subservice.all())
    instance.price = total_price  # Adjust this line if you need specific discount logic
    instance.save()