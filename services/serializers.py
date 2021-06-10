from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Tag, Vendor, vendor_directory_path

class TagCreateSerializer(serializers.Serializer):
    name = serializers.CharField()

class TagListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ('name',)

class TagSerializer(serializers.Serializer):
    id = serializers.UUIDField(validators = [UniqueValidator])

class VendorCreateSerializer(serializers.Serializer):
    name = serializers.CharField(validators = [UniqueValidator], required = True)
    service = serializers.ChoiceField(choices = Vendor.service_choices, required = True)
    tags = TagSerializer(many = True,required = False,)
    opening_time = serializers.TimeField(required = False, format = "%H:%M")
    closing_time = serializers.TimeField(required = False, format = "%H:%M")
    location = serializers.CharField(required = False,)
    cover = serializers.ImageField(required = False)
    Rating = serializers.DecimalField(max_digits = 2, decimal_places=1, read_only = True,)
    

class VendorListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Vendor
        fields = '__all__'