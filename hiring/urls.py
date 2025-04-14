from django.urls import path

from hiring.views import HiringView, DesignationView, OurTeamView

urlpatterns = [
    path('hiring_now/', HiringView.as_view(), name='Hiring'),
    path('designations/', DesignationView.as_view(), name='Designations'),
    path('our_team/', OurTeamView.as_view(), name='Team')
]
