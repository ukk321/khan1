from django.urls import path

from .views import ServiceView, SubServiceView, CategoryView, ContactUsView, ReplyCreateAPIView, BranchView, \
    CategoryAutocomplete, SubServicesAutocomplete,search_api,ProductAttributeView,HomePageView

urlpatterns=[
    path('collections/', ServiceView.as_view(), name='Service_View'),
    path('products/', SubServiceView.as_view(),name='SubService_View'),
    path('categories/',CategoryView.as_view(),name='Category_View'),
    path('contact-us/', ContactUsView.as_view(), name='contact-us-mail'),
    path('api/reply/', ReplyCreateAPIView.as_view(), name='reply-create'),
    path('branch/',BranchView.as_view(),name='branch-name'),
    path('category-autocomplete/', CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('subservices-autocomplete/', SubServicesAutocomplete.as_view(), name='subservices-autocomplete'),
    path('search/',search_api,name='search=api'),
    path('product-attributes/', ProductAttributeView.as_view(), name='product-attributes'),
    path('homepage/',HomePageView.as_view(),name='homepage-view')
]