from PIL import Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from booking.models import check_admin_call
from django.core.exceptions import ObjectDoesNotExist

CM_TO_INCH = 0.393701
INCH_TO_CM = 2.54


def validate_image_dimensions(value, is_new_instance=False):
    if value and is_new_instance:
        img = Image.open(value)
        width, height = img.size
        required_width = 350
        required_height = 175
        if width != required_width or height != required_height:
            raise ValidationError(
                "This image can't be uploaded. Please make sure the dimensions are Width 350 and Height 175.")


def fetch_service_data():
    from services.views import ServiceView
    import json
    from django.http import HttpRequest

    request = HttpRequest()
    request.method = 'GET'
    
    response = ServiceView.as_view()(request)
    response.render()

    service_data = json.loads(response.content.decode('utf-8'))['Collections']
    
    def filter_fields(data, is_in_product=False):
        filtered_data = []
        for item in data:
            filtered_item = {
                'name': item.get('name', ''),
                'image': item.get('image', ''),
                'link': item.get('link', '')
            }
            
            # Add is_new field only if inside the 'Products' level or deeper
            if is_in_product:
                filtered_item['is_new'] = item.get('is_new', False)
            
            # Recursively filter Categories
            if 'Categories' in item:
                filtered_item['Categories'] = filter_fields(item['Categories'], is_in_product=False)
            
            # Recursively filter Products (including sub-products)
            if 'Products' in item:
                filtered_item['Products'] = [
                    {
                        'name': product.get('name', ''),
                        'image': product.get('image', ''),
                        'link': product.get('link', ''),
                        'is_new': product.get('is_new', False),
                        'Products': filter_fields(product.get('Products', []), is_in_product=True)
                    }
                    for product in item['Products']
                ]
            filtered_data.append(filtered_item)
        return filtered_data

    # Sort service data and apply the filter_fields function
    sorted_service_data = sorted(service_data, key=lambda x: x.get('sort_order') or 0)
    filtered_service_data = filter_fields(sorted_service_data)
    return filtered_service_data




def update_navbar_content():
    try:
        from core.models import Page, PageComponent
        page = Page.objects.get(title='home_page')
        menu_component = PageComponent.objects.get(page_id=page, name='nav_links')
    except ObjectDoesNotExist:
        return

    try:
        from core.models import Content
        nav_bar_content = Content.objects.get(page_id=page, component_id=menu_component, name='menu')
    except Content.DoesNotExist:
        return

    service_data = fetch_service_data()

    nav_bar_content.hierarchcal_json = service_data
    nav_bar_content.save()


class BaseStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
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


class BranchModel(BaseStampedModel):
    name = models.CharField(max_length=250, null=False, blank=False, unique=True, default='Johar Town')
    address = models.CharField(max_length=250, null=False, blank=False)
    branch_contact = models.CharField(max_length=20, null=False, blank=False, unique=True)
    branch_owner = models.CharField(max_length=250, null=False, blank=False)
    owner_contact = models.CharField(max_length=20, null=False, blank=False, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="branch_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="branch_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Branch'
        verbose_name_plural = 'Branches'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)


class AttributeNameModel(BaseStampedModel):
    name=models.CharField(max_length=100,null=False,blank=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attribute_name_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attribute_name_updated"
                                   )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name='Attribute Name'
        verbose_name_plural='Attribute Names'
    
    def save(self,*args,**kwargs):
        user=check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by=user
        
        super().save(*args,**kwargs)



class AttributeValueModel(BaseStampedModel):
    attribute_name=models.ForeignKey('AttributeNameModel',on_delete=models.CASCADE,related_name='attribute_values')
    value=models.CharField(max_length=100, null=False,blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attribute_value_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="attribute_value_updated"
                                   )

    def __str__(self):
        return f'{self.attribute_name.name} : {self.value}'

    class Meta:
        verbose_name='Attribute Value'
        verbose_name_plural='Attribute Values'
        unique_together=('attribute_name','value')

    
    def save(self,*args,**kwargs):
        user=check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by=user
        
        super().save(*args,**kwargs)
        

class ProductAttribute(BaseStampedModel):
    product=models.ForeignKey('SubServicesModel',on_delete=models.CASCADE,related_name='product_attributes')
    attribute_value=models.ManyToManyField('AttributeValueModel',related_name='product_attributes')
    quantity=models.IntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_attribute_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_attribute_updated"
                                   )


    def __str__(self):
        return f'{self.product.name} - {self.attribute_value}'

    class Meta:
        verbose_name='Product Attribute'
        verbose_name_plural='Product Attributes'
    
    def save(self,*args,**kwargs):
        user=check_admin_call(kwargs)

        if not self.pk and not self.created_by:
            self.created_by=user
        
        super().save(*args,**kwargs)



class ServiceModel(BaseStampedModel):
    name = models.CharField(max_length=250, null=False, blank=False, unique=True, default=' ')
    heading = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price_range = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to='', null=True, blank=True)
    sort_order=models.IntegerField(null=True,blank=True,default=0)
    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE, null=True, blank=True,
                               related_name="services")
    link=models.CharField(max_length=100,blank=True,null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="service_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="service_updated"
                                   )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if self.pk:
            previous_instance=ServiceModel.objects.get(pk=self.pk)
            name_changed=previous_instance.name!=self.name
            image_changed=previous_instance.image!=self.image
            link_changed=previous_instance.image!=self.link
        else:
            name_changed=image_changed=link_changed=True

        if not self.pk and not self.created_by:
            self.created_by = user
        
        super().save(*args, **kwargs)

        if name_changed or image_changed or link_changed:        
            update_navbar_content()


class CategoryModel(BaseStampedModel):
    service = models.ForeignKey(ServiceModel, on_delete=models.CASCADE,
                                related_name="categories", null=True, blank=False,verbose_name="Collection")
    name = models.CharField(max_length=20, null=False, blank=False, unique=True, default=' ')
    image = models.ImageField(upload_to='', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link=models.CharField(max_length=100,blank=True,null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="category_created"
                                   )
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="category_updated"
                                   )
    sub_services = models.ManyToManyField('SubServicesModel', null=True, blank=True, related_name="categories",verbose_name="Products")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if self.pk:
            previous_instance=CategoryModel.objects.get(pk=self.pk)
            name_changed=previous_instance.name!=self.name
            image_changed=previous_instance.image!=self.image
            link_changed=previous_instance.link!=self.link
        else:
            name_changed= image_changed=link_changed=True

        if not self.pk and not self.created_by:
            self.created_by = user

        super().save(*args, **kwargs)

        if name_changed or image_changed or link_changed:
            update_navbar_content()


class SubServicesModel(BaseStampedModel):
    name = models.CharField(max_length=250, null=False, blank=False, unique=True, default=' ')
    is_new=models.BooleanField(default=False)
    heading = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(default=0, null=False, blank=True)
    discounted_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True)
    image = models.ImageField(upload_to='', null=True, blank=True, validators=[validate_image_dimensions])
    currency = models.CharField(max_length=250, null=True, blank=True)
    service = models.ForeignKey(ServiceModel, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="service",verbose_name="Collection")
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name="category_service",verbose_name="Category")
    subservice = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                   related_name='subservice_category',verbose_name="Product")
    branch = models.ForeignKey(BranchModel, on_delete=models.CASCADE, null=True, blank=True, related_name="SS_Branch")
    link=models.CharField(max_length=100,blank=True,null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="subservice_created")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="subservice_updated")

    def __str__(self):
        return self.name

    def clean(self):
        """
               Custom clean method to ensure subservice nesting is limited to 4 levels.
               """
        super().clean()

        # Validate subservice depth
        if self.subservice and self.check_depth(self.subservice) >= 4:
            raise ValidationError('Subservices can only be nested up to 4 levels.')

    def check_depth(self, subservice_instance):
        depth = 1
        current = subservice_instance
        while current.subservice:
            depth += 1
            current = current.subservice
            if depth >= 4:  # Check the condition here to stop early if it exceeds limits
                break
        return depth

    class Meta:
        verbose_name = 'Products'
        verbose_name_plural = 'Products'

    def save(self, *args, **kwargs):
        user = check_admin_call(kwargs)

        if self.pk:
            previous_instance=SubServicesModel.objects.get(pk=self.pk)
            name_changed=previous_instance.name!=self.name
            is_new_changed=previous_instance.is_new!=self.is_new
            link_changed=previous_instance.link!=self.link
        else:
            name_changed=True
            is_new_changed=True
            link_changed=True

        if not self.pk and not self.created_by:
            self.created_by = user

        self.full_clean()
        super().save(*args, **kwargs)
        

        if self.category:
            self.category.sub_services.add(self)

        if name_changed or is_new_changed or link_changed:
            update_navbar_content()


class ProductsImage(models.Model):
    product=models.ForeignKey(SubServicesModel,on_delete=models.CASCADE,related_name="images")
    image=models.ImageField(upload_to='')

    def __str__(self):
        return "%s" % (self.product.name)

class ContactUs(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False, default=' ')
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r'^[0-9]+$', 'Enter a valid phone number.')]
    )
    message = models.TextField(max_length=200, null=True, blank=False)
    choose_file = models.FileField(upload_to='images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'


class Reply(models.Model):
    contact = models.ForeignKey(ContactUs, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.contact.name} at {self.timestamp}"


class SearchSuggestion(BaseStampedModel):
    query=models.CharField(max_length=250)
    popularity=models.IntegerField(default=0)
    

    def __str__(self):
        return self.query


class SizeCategory(models.Model):
    name = models.CharField(max_length=100) # Sections - Top, Bottom

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural='Size Categories'

class Size(models.Model):
    size = models.CharField(max_length=10) # Small, 2/3Y
    category = models.ForeignKey(SizeCategory, on_delete=models.CASCADE, related_name="sizes")

    def __str__(self):
        return f"{self.size} ({self.category.name})"

class SizeAttribute(models.Model):
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="attributes")
    attribute_name = models.CharField(max_length=50) # Sleeve Length, etc
    value_in_cm = models.DecimalField(max_digits=5, decimal_places=1)

    def __str__(self):
        return f"{self.size}: {self.attribute_name}: {self.value_in_cm} cm"

    def value_in_inches(self):
        if self.value_in_cm is None:
            return None
        
        return round(float(self.value_in_cm) * CM_TO_INCH, 2)

    def get_value(self, unit="cm"):
        if unit == "inches":
            return self.value_in_inches()
        return self.value_in_cm

class ProductSizeAttribute(models.Model):
    product = models.ForeignKey('SubServicesModel', on_delete=models.CASCADE, related_name='size_attributes')
    size_attribute = models.ForeignKey('SizeAttribute', on_delete=models.CASCADE, related_name='product_size')

    def __str__(self):
        return f"{self.product.name} - {self.size_attribute.attribute_name}: {self.size_attribute.value_in_cm} cm"

    class Meta:
        unique_together = ('product', 'size_attribute')