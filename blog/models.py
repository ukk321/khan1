from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from booking.models import check_admin_call

# Create your models here.

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


class Tag(BaseStampedModel):
    name = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tag_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tag_updated")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class Blog(BaseStampedModel):
    title = models.CharField(max_length=200)
    content = RichTextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='images/',blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag ,blank=True)
    isApproved = models.BooleanField(default=False)
    isNewsletter=models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_updated")
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Blog'
        verbose_name_plural = 'Blogs'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user
        
        is_new_instance = self.pk is None
        previous_is_approved = None

        if not is_new_instance:
            previous_instance = Blog.objects.get(pk=self.pk)
            previous_is_approved = previous_instance.isApproved

        super().save(*args, **kwargs)


class NewsletterSubscriber(BaseStampedModel):
    email=models.EmailField(unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="newsletter_subscribers_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="newsletter_subscribers_updated")
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)