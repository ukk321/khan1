from rest_framework import serializers
from .models import *


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model=DesignationModel
        fields='__all__'


class HiringSerializer(serializers.ModelSerializer):
    position_applying_for = serializers.PrimaryKeyRelatedField(queryset=DesignationModel.objects.all())

    class Meta:
        model=HiringModel
        fields='__all__'


class OurTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model=OurTeamModel
        fields='__all__'
