from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from .models import ProductCategory, Tag, Vendor, vendor_directory_path, Schedule

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
    service = serializers.ChoiceField(choices = Vendor.ServiceChoices.choices, required = True)
    tags = TagSerializer(many = True,required = False,)
    #opening_time = serializers.TimeField(required = False, format = "%H:%M")
    #closing_time = serializers.TimeField(required = False, format = "%H:%M")
    location = serializers.CharField(required = False,)
    cover = serializers.ImageField(required = False)
    rating = serializers.DecimalField(max_digits = 2, decimal_places=1, read_only = True,)
    users = serializers.CharField(read_only = True,) 


class VendorRetrieveSerializer(serializers.Serializer):
    name = serializers.CharField(validators = [UniqueValidator], required = True)
    service = serializers.ChoiceField(choices = Vendor.ServiceChoices.choices, required = True)
    tags = TagSerializer(many = True, required = False,)
    #opening_time = serializers.TimeField(required = False, format = "%H:%M")
    #closing_time = serializers.TimeField(required = False, format = "%H:%M")
    location = serializers.CharField(required = False,)
    cover = serializers.ImageField(required = False)
    rating = serializers.DecimalField(max_digits = 2, decimal_places=1, read_only = True,)
    users = serializers.CharField(read_only = True,)

class VendorUpdateSerializer(serializers.Serializer):
    tags = TagSerializer(many = True, required = False)
    location = serializers.CharField(required = False)
    cover = serializers.ImageField(required = False)

class VendorListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many = True,)
    class Meta:
        model = Vendor
        fields = ('name', 'service','location','tags','rating',
                     'users','cover','date_created','date_updated',)           

class VendorScheduleSerializer(serializers.Serializer):
    id = serializers.UUIDField()

class ScheduleCreateSerializer(serializers.Serializer):
    vendor = VendorScheduleSerializer(read_only = True, required = False)
    weekday = serializers.ChoiceField(choices=Schedule.WeekdayChoices.choices,)
    from_hour = serializers.TimeField()
    to_hour = serializers.TimeField()
    closed_open = serializers.ChoiceField(choices = Schedule.StatusChoices.choices, read_only = True)
      
    #class Meta:
     #   validators = [
      #      UniqueTogetherValidator(queryset=Schedule.objects.all(),
       #                             fields = ['vendor','weekday'],
       #                             message = 'You have already created a schedule for this weekday')
        #]
    
class ScheduleListSerializer(serializers.ModelSerializer):
    vendor = serializers.CharField(source = 'vendor.name')
    weekday = serializers.ChoiceField(choices=Schedule.WeekdayChoices.choices,) #Get source
    class Meta:
        model = Schedule
        fields = ('vendor', 'weekday', 'from_hour','to_hour','closed_open')

class ScheduleRetrieveListSerializer(serializers.Serializer):
    vendor = VendorScheduleSerializer(read_only = True)
    weekday = serializers.ChoiceField(choices=Schedule.WeekdayChoices.choices,read_only = True,)
    from_hour = serializers.TimeField()
    to_hour = serializers.TimeField()
    closed_open = serializers.ChoiceField(choices = Schedule.StatusChoices.choices, read_only = True,)

class ScheduleRetrieveUpdateSerializer(serializers.Serializer):
    vendor = VendorScheduleSerializer(read_only = True)
    weekday = serializers.ChoiceField(choices=Schedule.WeekdayChoices.choices,read_only = True)
    from_hour = serializers.TimeField()
    to_hour = serializers.TimeField()
    closed_open = serializers.ChoiceField(choices = Schedule.StatusChoices.choices, read_only = True)


class VendorProductCategorySerializer(serializers.Serializer):
    id =serializers.UUIDField

class ProductCategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    vendor = VendorProductCategorySerializer(read_only = True)

class ProductCategoryListSerializer(serializers.Serializer):
    name = serializers.CharField()
    vendor = serializers.CharField(read_only = True, source = 'vendor.name')

class ProductCategoryRetrieveUpdateSerializer(serializers.Serializer):
    name = serializers.CharField()
    vendor = serializers.CharField(read_only = True, source = 'vendor.name')
    