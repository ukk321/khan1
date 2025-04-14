from django.urls import path

from policies import views
from policies.views import PolicyView, create_deal, delete_deal, fetch_all_deals_for_template, check_deal_name

urlpatterns=[
    path('policy/',PolicyView.as_view(),name='site-policy'),
    path('admin/create_deal/', create_deal, name='create_deal'),
    path('admin/fetch_deals/', views.fetch_deals, name='fetch_deals'),
    path('admin/fetch_all_deals_for_template/', fetch_all_deals_for_template, name='fetch_all_deals_for_template'),
    path('admin/check_deal_name/', check_deal_name, name='check_deal_name'),
    path('delete_deal/<int:deal_id>/', delete_deal, name='delete_deal'),
]