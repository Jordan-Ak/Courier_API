from rest_framework import serializers
from .models import Tags

class TagCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

class TagListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tags
        fields = ('name',)