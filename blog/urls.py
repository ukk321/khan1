from django.urls import path
from . import views

urlpatterns = [
    path('blogs/', views.blog_list, name='blog_list'),
    # path('create/', views.create_blog, name='create_blog'),
    path('post/<int:pk>/', views.blog_detail, name='blog_detail'),
    # path('<int:pk>/', views.update_blog, name='blog_edit'),
    # path('<int:pk>/', views.delete_blog, name='blog_delete'),
    path('subscribe_newsletter/',views.subscribe_newsletter,name='subscribe_newsletter'),
]