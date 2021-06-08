from rest_framework import serializers


class TagCreateSerializer(serializers.Serializer):
    tag = serializers.CharField()
    