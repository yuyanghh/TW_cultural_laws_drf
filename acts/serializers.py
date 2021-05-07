from acts.models import Act
from rest_framework import serializers


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'
