from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from utils.email_service import EmailService
from django.db import IntegrityError
from rest_framework import status


User=get_user_model()

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = '__all__'


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'


class ElementsSerializer(serializers.ModelSerializer):
    element_content = ContentSerializer(many=True)

    class Meta:
        model = Elements
        fields = ('id', 'name', 'component_id', 'page_id', 'client_id', 'created_by', 'updated_by',
                  'element_content')


class ComponentSerializer(serializers.ModelSerializer):
    component_elements = ElementsSerializer(many=True)

    class Meta:
        model = PageComponent
        fields = ('id', 'name', 'page_id', 'created_by', 'updated_by',
                  'component_elements')


class CompletePageSerializer(serializers.ModelSerializer):
    page_components = ComponentSerializer(many=True)

    class Meta:
        model = Page
        fields = (
            'id', 'title', 'url', 'created_at', 'updated_at', 'is_active', 'created_by', 'updated_by',
            'page_components')


class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True)
    name=serializers.CharField(required=False)

    class Meta:
        model=User
        fields=('email','password','name')

    def create(self,validated_data):
        try:
            user=User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('name','')
            )
            
            EmailService.send_email_with_template_key(
                template_key='Register_User',
                recipients=[user.email],
                context={
                'user': user
                }
            )
            return user
        
        except IntegrityError:
            raise serializers.ValidationError({'success':False,'message': 'Email address already exists. Please try a different email address.','data':None})

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)