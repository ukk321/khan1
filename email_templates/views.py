from rest_framework.generics import ListAPIView

from .models import EmailTemplate
from .serializers import EmailTemplateSerializer


class EmailTemplateView(ListAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
