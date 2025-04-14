"""
URL configuration for lacigal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

handler400 = 'core.views.custom_400_view'
handler403= 'core.views.custom_403_view'
handler404='core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('collection/', include('services.urls')),
    path('error/', include('error_logging.urls')),
    # path('hiring/',include('hiring.urls')),
    # path('testimonials/',include('testimonials.urls')),
    path('booking/',include('booking.urls')),
    path('email_templates/',include('email_templates.urls')),
    # path('policies/',include('policies.urls')),
    path('blog/',include('blog.urls'))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT_PATH)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
admin.site.site_header="Qafoor"
admin.site.site_title="Qafoor"
admin.site.index_title= "Qafoor"
