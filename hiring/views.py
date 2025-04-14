from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response

from hiring.models import DesignationModel, OurTeamModel
from hiring.serializers import HiringSerializer, DesignationSerializer, OurTeamSerializer
from hiring.utils import HiringNotification
from lacigal import settings


class HiringView(CreateAPIView):
    serializer_class = HiringSerializer

    def post(self, request, *args, **kwargs):
        serialized_data = HiringSerializer(data=request.data)
        if serialized_data.is_valid():
            applicant_details = {
                'name': serialized_data.validated_data.get('name', ''),
                'email': serialized_data.validated_data.get('email', ''),
                'message': serialized_data.validated_data.get('message', ''),
                'position_applying_for': serialized_data.validated_data.get('position_applying_for', ''),
                # Add more fields as needed
            }

            if applicant_details['email']:
                HiringNotification.hiring_mail_user(
                    email=applicant_details['email'],

                    applicant_details=applicant_details
                )

            # Always send email to admin
            HiringNotification.send_mail_to_admin(
                email=settings.ADMINS[0][1],

                applicant_details=applicant_details
            )

            serialized_data.save()

            response = {'success': True,'message':' Hiring Created Successfully', 'data': serialized_data.data}
            return Response(response, status.HTTP_201_CREATED)
        else:
            response = {'success': False, 'message': serialized_data.errors, 'data':None}
            return Response(response,status.HTTP_400_BAD_REQUEST)


class DesignationView(ListAPIView):
    serializer_class = DesignationSerializer
    queryset = DesignationModel.objects.all()


class OurTeamView(ListAPIView):
    serializer_class = OurTeamSerializer

    def get_queryset(self):
        queryset = OurTeamModel.objects.filter(is_active=True)
        return queryset
