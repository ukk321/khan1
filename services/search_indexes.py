from haystack import indexes
from .models import ServiceModel,CategoryModel,SubServicesModel

class ServiceModelIndex(indexes.SearchIndex,indexes.Indexable):
    text= indexes.EdgeNgramField(document=True,use_template=True)
    name=indexes.EdgeNgramField(model_attr='name')
    description=indexes.EdgeNgramField(model_attr='description')
    
    def get_model(self):
        return ServiceModel

    def index_queryset(self,using=None):
        return self.get_model().objects.all()


class CategoryModelIndex(indexes.SearchIndex,indexes.Indexable):
    text= indexes.EdgeNgramField(document=True,use_template=True)
    name=indexes.EdgeNgramField(model_attr='name')
    description=indexes.EdgeNgramField(model_attr='description')

    def get_model(self):
        return CategoryModel
    
    def index_queryset(self,using=None):
        return self.get_model().objects.all()

class SubServiceModelIndex(indexes.SearchIndex,indexes.Indexable):
    text=indexes.EdgeNgramField(document=True,use_template=True)
    name=indexes.EdgeNgramField(model_attr='name')
    description=indexes.EdgeNgramField(model_attr='description')
    price = indexes.FloatField(model_attr='price')
    service=indexes.CharField(model_attr='service__name',faceted=True)
    category=indexes.CharField(model_attr='category__name',faceted=True)
    attribute_values=indexes.MultiValueField()
    product_image_urls = indexes.MultiValueField(indexed=False, null=True)
    parent_subservice_name = indexes.EdgeNgramField(model_attr='subservice__name')

    def get_model(self):
        return SubServicesModel
    
    def prepare_attribute_values(self, obj):
        attribute_values = []
        for product_attribute in obj.product_attributes.all():
            for attribute in product_attribute.attribute_value.all():
                attribute_name = attribute.attribute_name.name
                attribute_value = attribute.value
                attribute_values.append(f"{attribute_name}: {attribute_value}")
        return attribute_values

    def prepare_product_image_urls(self,obj):
        return [image.image.url for image in obj.images.all()][:1]

    def index_queryset(self,using=None):
        return self.get_model().objects.all()


# class SearchSuggestionModelIndex(indexes.SearchIndex,indexes.Indexable):
#     text=indexes.EdgeNgramField(document=True,use_template=True)
#     query=indexes.EdgeNgramField(model_attr='query')
#     popularity=indexes.IntegerField(model_attr='popularity')
    
#     def get_model(self):
#         return SearchSuggestion
    
#     def index_queryset(self,using=None):
#         return self.get_model().objects.all()
        