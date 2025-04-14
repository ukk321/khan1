from dal import autocomplete
from django.db.models import Q
from rest_framework import filters, generics
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from haystack.query import SearchQuerySet
from lacigal import settings
from .models import ServiceModel, CategoryModel,SubServicesModel, Reply, BranchModel,ProductsImage,SearchSuggestion
from .serializers import ServiceSerializer, SubServicesSerializer, CategorySerializer, ContactUsSerializer, \
    ReplySerializer, BranchSerializer, ProductsImageSerializer
from utils.email_service import EmailService
from django.http import JsonResponse
from utils.custom_contain import CustomContain

class FirstLetterFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        letter = request.query_params.get('first_letter')
        category_id = request.query_params.get('category_id')
        service_id = request.query_params.get('service_id')

        if letter:
            queryset = queryset.filter(Q(name__istartswith=letter) | Q(name__istartswith=letter.upper()))

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if service_id:
            queryset = queryset.filter(service__id=service_id)

        return queryset


class HomePageView(APIView):
    def get(self, request):
        whats_new = SubServicesModel.objects.filter(service=1).order_by("-created_at")[:10] # products of new in
        shop_by_category = CategoryModel.objects.all()[:8] # all categories
        trending = SubServicesModel.objects.all().order_by("-created_at")[:10] # all recent products

        more_to_explore = [] # first category of all collections
        for service in ServiceModel.objects.all():
            first_category = service.categories.filter(image__isnull=False).first()
            if first_category:
                more_to_explore.append({
                    "name": first_category.name,
                    "description": first_category.description,
                    "image": first_category.image.url if first_category.image else ""
                })

        serialized_whats_new = SubServicesSerializer(whats_new, many=True).data
        serialized_shop_by_category = CategorySerializer(shop_by_category, many=True).data
        serialized_trending = SubServicesSerializer(trending, many=True).data

        data = {
            "whats_new": [
                {
                    "name": product['name'],
                    "image": product['images'][0]['image'] if product['images'] else None,
                } for item in serialized_whats_new for product in item.get('Products', [])
            ],
            "shop_by_category": [
                {"name": item['name'], "image": item['image']} for item in serialized_shop_by_category
            ],
            "trending": [
                   {
                    "name": product['name'],
                    "image": product['images'][0]['image'] if product['images'] else None,
                } for item in serialized_trending for product in item.get('Products', [])
            ],
            "more_to_explore": more_to_explore,
        }

        return Response(data)


class BranchView(ListAPIView):
    serializer_class = BranchSerializer
    queryset = BranchModel.objects.all()

class ProductImagesView(generics.ListAPIView):
    serializer_class=ProductsImageSerializer

    def get_query(self):
        product_id=self.kwargs.get('subservice_id')
        return ProductsImage.objects.filter(product_id=product_id)


class ProductAttributeView(APIView):
    def get(self, request, *args, **kwargs):
        attribute_values = request.query_params.getlist('attribute')
        collection_name = request.query_params.get('collection')

        if not collection_name:
            return Response({"error": "Please specify a collection to filter."})

        sqs = SearchQuerySet().models(SubServicesModel).filter(service__name=collection_name)

        categories = SearchQuerySet().models(CategoryModel).filter(name__in=attribute_values).values_list('name', flat=True)
        non_category_attributes = [attr for attr in attribute_values if attr not in categories]

        if categories:
            sqs = sqs.filter(category__name__in=categories)
        for attr in non_category_attributes:
            sqs = sqs.filter(attribute_values=attr)

        if not attribute_values:
            attribute_counts = {}
            
            for result in sqs:
                if result.object.subservice:
                    for attribute in result.attribute_values:
                        name, value = attribute.split(": ")
                        attribute_counts.setdefault(name, {}).setdefault(value, 0)
                        attribute_counts[name][value] += 1
                    
                    category_name = result.category
                    if category_name:
                        attribute_counts.setdefault("Category", {}).setdefault(category_name, 0)
                        attribute_counts["Category"][category_name] += 1

            return Response({
                'success': True,
                'message': 'Collection Filtered Successfully',
                'data': {
                    'collection': collection_name,
                    'attributes': [{'name': k, 'values': v} for k, v in attribute_counts.items()]
                }
            })

        product_data = [
            {
                'product_id': result.object.id,
                'product_name': result.object.name,
                'price': result.object.price,
                'image': result.object.images.first().image.url if result.object.images.exists() else '',
                'category': result.category
            }
            for result in sqs if result.object.subservice
        ]

        return Response({
            'success': True,
            'message': 'Attributes Filtered Successfully',
            'data': product_data
        })


class SubServiceView(ListAPIView):
    serializer_class = SubServicesSerializer
    queryset = SubServicesModel.objects.all().order_by('id')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        queryset = super().get_queryset()
        parent_id = self.request.query_params.get('id')

        if parent_id:
            queryset = queryset.filter(id=parent_id)
        else:
            queryset = queryset.filter(subservice__isnull=True)

        return queryset

    def child_sorting(self,parent,sort_by):
        child_subservices=SubServicesModel.objects.filter(subservice=parent)

        if sort_by=='name_asc':
            return child_subservices.order_by('name')
        elif sort_by=='name_desc':
            return child_subservices.order_by('-name')
        elif sort_by=='price_low_high':
            return child_subservices.order_by('price')
        elif sort_by=='price_high_low':
            return child_subservices.order_by('-price')
        elif sort_by=='date_old_new':
            return child_subservices.order_by('created_at')
        elif sort_by=='date_new_old':
            return child_subservices.order_by('-created_at')
        
        else:
            return child_subservices

    def get(self, request):
        queryset = self.get_queryset()
        sort_by = self.request.query_params.get('sort_by', 'default')

        serialized_data = []
        for parent in queryset:
            sorted_child_products = self.child_sorting(parent, sort_by)
            
            parent_data = self.get_serializer(parent).data
            parent_data['Products'] = SubServicesSerializer(sorted_child_products, many=True).data
            
            serialized_data.append(parent_data)

        final_output = {'Products': serialized_data}
        return Response(final_output)


class ServiceView(ListAPIView):
    serializer_class = ServiceSerializer
    queryset = ServiceModel.objects.all().order_by('name')
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, FirstLetterFilterBackend]
    search_fields = ['name', 'heading', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        service_id = self.request.query_params.get('id')
        if service_id:
            queryset = queryset.filter(id=service_id)
        return queryset.order_by('id')

    def get(self, request, *args, **kwargs):
        attribute_values = request.query_params.getlist('attribute')
        collection_name = request.query_params.get('collection')
        start_price=request.query_params.get('start_price')
        end_price=request.query_params.get('end_price')

        if not collection_name:
            services_queryset = self.filter_queryset(self.get_queryset())
            serialized_data = self.get_serializer(services_queryset, many=True).data
            serialized_data.sort(key=lambda x: x['name'])
            final_output = {'Collections': serialized_data}
            return Response(final_output)
        
        sqs = SearchQuerySet().models(SubServicesModel).filter(service__name=collection_name)

        if attribute_values:
            categories = SearchQuerySet().models(CategoryModel).filter(name__in=attribute_values).values_list('name', flat=True)
            non_category_attributes = [attr for attr in attribute_values if attr not in categories]

            if categories:
                sqs = sqs.filter(category__name__in=categories)
            for attr in non_category_attributes:
                sqs = sqs.filter(attribute_values=attr)
        
        if start_price and end_price:
            sqs=sqs.filter(price__gte=start_price,price__lte=end_price)

            product_data = [
                {
                    'product_id': result.object.id,
                    'product_name': result.object.name,
                    'price': result.object.price,
                    'image': result.object.images.first().image.url if result.object.images.exists() else '',
                    'category': result.category
                }
                for result in sqs if result.object.subservice
            ]

            return Response({
                'success': True,
                'message': 'Attributes Filtered Successfully',
                'data': product_data
            })
        
        attribute_counts = {}
        for result in sqs:
            if result.object.subservice:
                for attribute in result.attribute_values:
                    name, value = attribute.split(": ")
                    attribute_counts.setdefault(name, {}).setdefault(value, 0)
                    attribute_counts[name][value] += 1
                
                category_name = result.category
                if category_name:
                    attribute_counts.setdefault("Category", {}).setdefault(category_name, 0)
                    attribute_counts["Category"][category_name] += 1

        product_data = [
            {
                'product_id': result.object.id,
                'product_name': result.object.name,
                'price': result.object.price,
                'images': [image.image.url for image in result.object.images.all()] if hasattr(result.object, 'images') and result.object.images else [],
                'category': result.category
            }
            for result in sqs if result.object.subservice
        ]

        return Response({
            'success': True,
            'message': 'Collection Filtered Successfully',
            'data': {
                'collection': collection_name,
                'filters': [{'name': k, 'values': v} for k, v in attribute_counts.items()],
                'categories':[
            {
                'name': category.name,
                'image': category.image.url if category.image else ''
            }
            for category in CategoryModel.objects.filter(category_service__service__name=collection_name).distinct()
        ],
                'products': product_data
            }
        })



class CategoryView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = CategoryModel.objects.all()
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, FirstLetterFilterBackend]
    search_fields = ['name']

    def get_queryset(self):
        
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('id')
        if category_id:
            queryset = queryset.filter(id=category_id)
        return queryset.order_by('id')

    def get(self, request,*args,**kwargs):
        attribute_values = self.request.query_params.getlist('category_name')
        if attribute_values:
            queryset = self.get_queryset().filter(name__in=attribute_values)
        else:
            queryset = self.get_queryset()
        category_queryset = self.filter_queryset(queryset)
        serialized_data = CategorySerializer(category_queryset, many=True).data
        final_output = {'Categories': serialized_data}
        return Response(final_output)


class ContactUsView(CreateAPIView):
    serializer_class = ContactUsSerializer

    def post(self, request, *args, **kwargs):
        serialized_data = ContactUsSerializer(data=request.data)
        if serialized_data.is_valid():

            name = serialized_data.validated_data.get('name', '')
            message = serialized_data.validated_data.get('message', '')

            if 'email' in self.request.data and self.request.data['email']:
                EmailService.send_email_with_template_key(
                    template_key='Contact_Us_Client',
                    recipients=[self.request.data['email']],
                    context={'name': name, 'message': message},
                )

            contact_instance = serialized_data.save()

            EmailService.send_email_with_template_key(
                template_key='Contact_Us_Admin',
                recipients=[settings.ADMINS[0][1]],
                context={'name': name, 'message': message, 'inquiry_id': contact_instance.pk},
            )
            response = {'success': True,'message': 'Contact Us Created Successfully', 'data': serialized_data.data}
            return Response(response,status=status.HTTP_201_CREATED)
        else:
            response = {'success': False, 'message': serialized_data.errors,'data':None}
            return Response(response,status=status.HTTP_400_BAD_REQUEST)


class ReplyCreateAPIView(generics.CreateAPIView):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return CategoryModel.objects.none()

        qs = CategoryModel.objects.all()

        service = self.forwarded.get('service', None)
        if service:
            qs = qs.filter(service__id=service)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class SubServicesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SubServicesModel.objects.all()

        service_id = self.forwarded.get('service', None)
        category_id = self.forwarded.get('category', None)

        if service_id:
            qs = qs.filter(service__id=service_id)
        if category_id:
            qs = qs.filter(category__id=category_id)

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs if qs.exists() else SubServicesModel.objects.none()


def search_api(request):
    query = request.GET.get('q', '')
    start_index = int(request.GET.get('startIndex', 0))
    items_per_page = int(request.GET.get('itemsPerPage', 6))

    if not query:
        return JsonResponse({
            "totalItems": 0,
            "itemsPerPage": items_per_page,
            "currentItemCount": 0,
            "totalCategories": 0,
            "suggestions": [],
            "categories": [],
            "items": [],
        }, status=200)

    results = SearchQuerySet().models(SubServicesModel).filter(content__contains=query).load_all()

    total_items = len(results)

    es_suggestions = SearchQuerySet().models(SubServicesModel).filter(
        Q(name=CustomContain(query)) | Q(description=CustomContain(query))
    ).load_all()
    
    es_suggestions_list = [result.object.name for result in es_suggestions][:5]

    combined_suggestions = list(es_suggestions_list)

    categories = SearchQuerySet().models(CategoryModel)[:5]

    categories_list = [
        {
            "category_id": category.object.id,
            "title": category.object.name,
            "link": f"/collections/{category.object.id}",
            "image": category.object.image.url if category.object.image else ""
        }
        for category in categories
    ]

    paginated_results = results[start_index:start_index + items_per_page]

    
    items = [
        {
            "product_id": result.object.id,
            "title": result.object.query if isinstance(result.object, SearchSuggestion) else result.object.name,
            "description": result.object.query if isinstance(result.object, SearchSuggestion) else result.object.description,
            "link": f"/products/{result.object.id}",
            "price": str(result.object.price) if isinstance(result.object, SubServicesModel) else "0",
            "image_link": result.product_image_urls[0] if result.product_image_urls else '',
        }
        for result in paginated_results
        if result.product_image_urls and result.product_image_urls[0]
    ]

    total_items = len(items)
    current_item_count = len(items)

    response = {
        "totalItems": total_items,
        "itemsPerPage": items_per_page,
        "currentItemCount": current_item_count,
        "totalCategories": len(categories_list),
        "suggestions": combined_suggestions,
        "categories": categories_list,
        "items": items,
    }

    return JsonResponse(response)
