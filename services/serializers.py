from rest_framework import serializers

from .models import *


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchModel
        fields = "__all__"


class ProductsImageSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source='product.name',read_only=True)

    class Meta:
        model=ProductsImage
        fields=['id','product','product_name','image']

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name=serializers.CharField(source='attribute_name.name',read_only=True)

    class Meta:
        model=AttributeValueModel
        fields=['id','attribute_name','value']


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_values=AttributeValueSerializer(many=True,source='attribute_value')

    class Meta:
        model=ProductAttribute
        fields=['id','quantity','attribute_values']


class SizeAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model=SizeAttribute
        fields=['attribute_name','value_in_cm','value_in_inches']


class SizeSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.name',read_only=True)
    attributes=SizeAttributeSerializer(many=True,source='attributes')

    class Meta:
        model=Size
        fields=['id','size','category__name','attributes']


class SubServicesSerializer(serializers.ModelSerializer):
    Products = serializers.SerializerMethodField()
    images=ProductsImageSerializer(many=True,read_only=True)
    attributes=ProductAttributeSerializer(many=True,read_only=True,source='product_attributes')
    sizes=serializers.SerializerMethodField()

    class Meta:
        model = SubServicesModel
        fields = (
            'id', 'name', 'is_new','heading', 'description', 'price', 'discounted_price', 'image', 'currency',
            'Products','images','attributes','sizes','link')

    def get_Products(self, obj):
        product = obj.subservice_category.all()
        return self.__class__(product, many=True).data
    
    def get_sizes(self,obj):
        product_sizes=ProductSizeAttribute.objects.filter(product=obj).select_related('size_attribute__size')
        distinct_sizes={psa.size_attribute.size for psa in product_sizes}

        serialized_sizes=[]
        for size in distinct_sizes:
            size_attributes=size.attributes.all()
            serialized_size={
                'id':size.id,
                'size':size.size,
                'section':size.category.name,
                'attributes':SizeAttributeSerializer(size_attributes,many=True).data
            }
            serialized_sizes.append(serialized_size)
        
        return serialized_sizes

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class CategorySerializer(serializers.ModelSerializer):
    Products = serializers.SerializerMethodField()

    class Meta:
        model = CategoryModel
        fields = ('id', 'name','image', 'description', 'Products','link')

    def get_Products(self, instance):
        sub_services_queryset = instance.sub_services.filter(subservice_id__isnull=True)  # Fetch only root nodes
        return SubServicesSerializer(sub_services_queryset, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class ServiceSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    branch = BranchSerializer()

    class Meta:
        model = ServiceModel
        fields = ('id', 'name', 'heading', 'description', 'price_range', 'image', 'branch','link', 'sort_order','categories')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['Categories']=representation.pop('categories')
        return representation


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ['id', 'contact', 'message', 'timestamp']