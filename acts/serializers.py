from acts.models import Act
from acts.models import Article
from acts.models import Legislation
from rest_framework import serializers


class ActSerializer(serializers.ModelSerializer):
    class Meta:
        model = Act
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class LegislationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislation
        fields = '__all__'
