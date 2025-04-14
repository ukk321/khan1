from rest_framework import serializers

from testimonials.models import TestimonialModel, SocialHandleModel


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model=TestimonialModel
        fields='__all__'


class SocialHandleSerializer(serializers.ModelSerializer):
    class Meta:
        model=SocialHandleModel
        fields='__all__'
