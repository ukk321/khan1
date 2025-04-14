from django.urls import path

from testimonials.views import TestimonialView, SocialHandleView

urlpatterns=[
    path('feedback/',TestimonialView.as_view(),name="client_testimonials"),
    path('social-accounts',SocialHandleView.as_view(),name='admin-accounts')
]