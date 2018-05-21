from rest_framework import serializers
from .models import API, APIDependency

class APISimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = API
        fields = ('name', 'url', 'type')
        read_only_fields = ('updated',)

class APIDependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIDependency
        fields = ('dependency',)

    dependency = APISimpleSerializer()

class APISerializer(serializers.ModelSerializer):
    class Meta:
        model = API
        fields = ('name', 'url', 'type', 'dependencies')
        read_only_fields = ('updated',)

    dependencies = APIDependencySerializer(many=True)
