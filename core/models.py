import json
import os

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from booking.models import check_admin_call


class BaseStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='%(class)s_created_by', default="'%(class)s_created_by")
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


class Page(BaseStampedModel):
    """The Page model is a representation of a web page and inherits from BaseStampedModel. It includes fields for
    the page's title, URL, and information about the users who created and last updated the page."""
    title = models.CharField(max_length=250, unique=True, null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="page_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="page_updated"
                                   )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class PageComponent(BaseStampedModel):
    """The PageComponent model extends the BaseStampedModel and represents a component associated with a web page."""
    name = models.CharField(max_length=250, unique=True, null=True, blank=True)
    page_id = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_components', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="component_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="component_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Page Component'
        verbose_name_plural = 'Page Components'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class Elements(BaseStampedModel):
    """The Elements model extends the BaseStampedModel and represents individual elements associated with a web page
    component."""
    name = models.CharField(max_length=500, null=True, blank=True)
    component_id = models.ForeignKey(PageComponent, on_delete=models.CASCADE, related_name='component_elements',
                                     null=True, blank=True)
    page_id = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_elements', null=True, blank=True)
    client_id = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="element_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="element_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Element'
        verbose_name_plural = 'Elements'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class Languages(BaseStampedModel):
    """The Languages model extends the BaseStampedModel and represents different languages."""
    name = models.CharField(max_length=250, default=0, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="language_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="language_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user
        super().save(*args, **kwargs)


def send_data_to_json(self, update=False, create=False):
    # Initialize S3 resource
    s3 = boto3.resource('s3',
                        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                        )
    bucket_name = settings.JSON_AWS_S3_BUCKET_NAME
    local_file_path = 'core/datafile.json'
    s3_file_key = 'data/datafile.json'

    # Download file from S3
    try:
        s3.Bucket(bucket_name).download_file(s3_file_key, local_file_path)
    except ClientError:
        return False

    # Get the absolute path to the current directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'datafile.json')

    # Read JSON file
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}  # Initialize an empty dictionary if file not found
    except json.JSONDecodeError:
        return False

    # Define a helper function to update the item
    def update_item(item, name, description, hierarchy_json_data, image_url, link, extras, content_order):
        item["name"] = name
        item["description"] = description
        item["json_data"] = hierarchy_json_data
        item["image"] = image_url
        item["link"] = link
        item["extras"] = extras
        item["content_order"] = content_order

    component_page_names = PageComponent.objects.values_list('name', flat=True)

    component_names = list(set(component_page_names))

    storage_bucket_name = settings.AWS_STORAGE_BUCKET_NAME

    if self.component_id.name in component_names:
        # Ensure that the component name exists in the data; if not, initialize an empty list
        if self.component_id.name not in data:
            data[self.component_id.name] = []

        item_found = False
        
        for i in data.get(self.component_id.name, []):
            if self.component_id.name == 'nav_links':
                data['nav_links'] = self.hierarchcal_json
                item_found = True
            elif i.get('id') == str(self.pk):
                updated_image_url = f"https://{storage_bucket_name}.s3.amazonaws.com/{self.content_image}"
                update_item(
                    i,
                    name=self.name,
                    description=self.content_value,
                    hierarchy_json_data=self.hierarchcal_json if self.component_id.name == 'nav_links' else None,
                    image_url=updated_image_url,
                    link=self.content_url,
                    extras=self.extras,
                    content_order=self.content_order
                )
                item_found = True

        # If no item was found, append a new one (for create operation)
        if not item_found:
            new_item = {
                "id": str(self.pk),
                "name": self.name,
                "description": self.content_value,
                "image": f"https://{storage_bucket_name}.s3.amazonaws.com/{self.content_image}",
                "link": self.content_url,
                "extras": self.extras,
                "content_order": self.content_order
            }
            data[self.component_id.name].append(new_item)

        # Sort the data by content_order
        data[self.component_id.name].sort(key=lambda x: x.get('content_order', float('inf')))

    # Save the updated file
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
    except IOError:
        return False

    # Upload the file to S3
    try:
        s3.Bucket(bucket_name).upload_file(local_file_path, s3_file_key)
    except ClientError:
        return False

    return True


class Content(BaseStampedModel):
    """The Content model extends the BaseStampedModel and represents the content associated with individual elements
    on a web page."""
    Element_Types = [
        ('Image', 'Image'),
        ('Text', 'Text'),
        ('Url', 'Url'),
    ]

    type = models.CharField(max_length=50, choices=Element_Types, null=True, blank=True)
    element_id = models.ForeignKey(Elements, on_delete=models.CASCADE, related_name='element_content', null=True,
                                   blank=True)
    language_id = models.ForeignKey(Languages, on_delete=models.CASCADE, default=0,
                                    related_name='language_content', null=True, blank=True)
    page_id = models.ForeignKey(Page, on_delete=models.CASCADE, default=1, related_name='page_content', null=True,
                                blank=True)
    component_id = models.ForeignKey(PageComponent, on_delete=models.CASCADE, related_name='page_content', null=True,
                                     blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    content_value = models.TextField(null=True, blank=True)
    hierarchcal_json = models.JSONField(null=True, blank=True)
    content_image = models.ImageField(upload_to='', null=True, blank=True)
    content_url = models.URLField(null=True, blank=True)
    extras = models.CharField(max_length=255, null=True, blank=True)
    content_order = models.IntegerField(null=True, blank=True,default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="content_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="content_updated"
                                   )

    def save(self, *args, **kwargs):
        is_for_update = False
        if self.pk:
            is_for_update = True
            send_data_to_json(self, update=True, create=False)
        super().save(*args, **kwargs)

        if self.component_id and not is_for_update:
            send_data_to_json(self, update=False, create=True)