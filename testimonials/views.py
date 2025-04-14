from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response

from lacigal import settings
from testimonials.models import TestimonialModel, validate_image_size, validate_video_size, SocialHandleModel
from testimonials.serializers import TestimonialSerializer, SocialHandleSerializer
from testimonials.utils import FeedbackNotification


class TestimonialView(CreateAPIView):
    queryset = TestimonialModel.objects.filter(isApproved=True)
    serializer_class = TestimonialSerializer

    def post(self, request, *args, **kwargs):
        serialized_data = TestimonialSerializer(data=request.data)
        if serialized_data.is_valid():
            # Check file size before saving
            file = request.FILES.get('file')
            if file:
                if file.name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    validate_image_size(file)
                elif file.name.endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    validate_video_size(file)

            feedback_details = {
                'name': serialized_data.validated_data.get('name', ''),
                'email': serialized_data.validated_data.get('email', ''),
                'message': serialized_data.validated_data.get('message', ''),
                # Add more fields as needed
            }

            if feedback_details['email']:
                FeedbackNotification.feedback_mail_user(
                    email=feedback_details['email'],
                    feedback_details=feedback_details
                )

            FeedbackNotification.send_mail_to_admin(
                email=settings.ADMINS[0][1],
                applicant_details=feedback_details
            )

            serialized_data.save()

            response = {'success': True,'message': 'Testimonial Created Successfully', 'data': serialized_data.data}
            return Response(response,status=status.HTTP_201_CREATED)
        else:
            response = {'success': False, 'message': serialized_data.errors,'data':None}
            return Response(response,status=status.HTTP_400_BAD_REQUEST)


class SocialHandleView(ListAPIView):
    serializer_class = SocialHandleSerializer

    def get_queryset(self):
        queryset = SocialHandleModel.objects.filter(is_active=True)
        return queryset

