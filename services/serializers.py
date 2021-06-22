from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from .models import CustomerCart, Product, ProductCategory, Rating, Tag, Vendor, vendor_directory_path, Schedule

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

class VendorProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()

class ProductCategoryProductSerializer(serializers.Serializer):
    id = serializers.UUIDField()

class ProductCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required = True,)
    detail = serializers.CharField(required = False)
    price = serializers.DecimalField(required = True,max_digits=10, decimal_places=2,)
    looks = serializers.ImageField(required = False)
    product_category = ProductCategoryProductSerializer(default = 'foods',)
    vendor = VendorProductSerializer(read_only = True)
    
class ProductListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('name', 'detail','price','looks','product_category','vendor',)

class ProductVendorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('name', 'detail','price','looks','product_category','vendor',)

class ProductRetrieveUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required = False)
    detail = serializers.CharField(required = False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required = False)
    looks = serializers.ImageField(required = False)
    product_category = ProductCategoryProductSerializer(required = False)
    vendor = VendorProductSerializer(read_only = True)

class VendorRatingSerializer(serializers.Serializer):
    id = serializers.UUIDField()

class UserRatingSerializer(serializers.Serializer):
    id = serializers.UUIDField()

class RatingCreateSerializer(serializers.Serializer):
    vendor_rated = VendorRatingSerializer()
    who_rated = UserRatingSerializer()
    rating = serializers.IntegerField()

class RatingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('vendor_rated', 'who_rated', 'rating')

class RatingListUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('vendor_rated', 'who_rated', 'rating',)

class RatingRetrieveSerializer(serializers.Serializer):
    vendor_rated = VendorRatingSerializer()
    who_rated = UserRatingSerializer()
    rating = serializers.IntegerField()

class RatingUpdateSerializer(serializers.Serializer):
    rating = serializers.IntegerField


class ProductCartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2,)
    looks = serializers.ImageField()

class VendorCartSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()

class CustomerCartCreateSerializer(serializers.Serializer):
    product = ProductCartSerializer()
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    ordered = serializers.BooleanField(default = False,)
    ordered_time =serializers.TimeField(read_only = True)
    delivered_time = serializers.TimeField(read_only = True)
    vendor = VendorCartSerializer()
    user = serializers.CharField(read_only = True)

class CustomerCartVendorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerCart
        fields = ('product', 'quantity', 'total_price','ordered','ordered_time',
                  'delivered_time','vendor','date_created')

class CustomerCartUserListSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only = True)
    product = ProductCartSerializer()
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    ordered = serializers.BooleanField(default = False)
    ordered_time =serializers.TimeField(read_only = True)
    delivered_time = serializers.TimeField(read_only = True)
    vendor = VendorCartSerializer()
    user = serializers.CharField(read_only = True)

class CustomerCartUserRetrieveSerializer(serializers.Serializer):
    product = ProductCartSerializer(read_only = True)
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    vendor = VendorCartSerializer(source = 'name', read_only = True)
    

'''    
class CustomerOrderCreateSerializer(serializers.Serializer):
    product = ProductCustomerSerializer()
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    ordered = serializers.BooleanField(read_only = True)
    user = serializers.CharField(read_only = True)
    vendor = VendorCustomerSerializer(read_only = True)
    
class CustomerOrderCartSerializer(serializers.Serializer):
    product = ProductCustomerSerializer()
    quantity = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only = True)
    ordered = serializers.BooleanField(read_only = True)
    user = serializers.CharField(read_only = True)
    vendor = VendorCustomerSerializer(read_only = True)

class CustomerCartRetrieveUpdateSerializer(serializers.Serializer):
    products = CustomerOrderCartSerializer()
    ordered = serializers.BooleanField(read_only = True)
    ordered_time = serializers.TimeField(read_only = True)
    delivered_time = serializers.TimeField(read_only = True)
    final_price = serializers.DecimalField(max_digits = 10, decimal_places= 2, read_only = True)
    user = serializers.CharField(read_only = True)
'''    
     

