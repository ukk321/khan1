from rest_framework import serializers

from policies.models import PolicyModel, DealModel


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model=PolicyModel
        fields='__all__'


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model=DealModel
        fields='__all__'
