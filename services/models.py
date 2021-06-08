from django.db import models
from common.models import BaseModel

# Create your models here.

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/vendor_<id>/<filename>
    return 'vendor_{0}/{1}'.format(instance.user.id, filename)

class Tags(BaseModel, models.Model):
    name = models.CharField(max_length = 25,)

    def __str__(self):
        return self.name

class Services(BaseModel, models.Model):
    RESTAURANT = 'REST'
    PARTY = 'PARTY'
    PHARMACY = 'PHAR'
    GROCERIES = 'GRO'
    CLOTHING = 'CLOTH'
    service_choices = [
        (RESTAURANT, 'restaurant'),
        (PARTY, 'party'),
        (PHARMACY, 'pharmacy'),
        (GROCERIES, 'groceries'),
        (CLOTHING, 'clothing'),
    ]

    name = models.CharField(max_length = 150,)
    service = models.CharField(max_length = 6, choices=service_choices)
    tags = models.ManyToManyField(Tags)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    location = models.CharField(max_length = 200)
    cover = models.ImageField(upload_to=vendor_directory_path)
    Rating = models.DecimalField(decimal_places=1, editable=False, max_digits = 2)

    def __str__(self):
        return self.name

class Location(BaseModel, models.Model):
    pass

class ProductCategory(BaseModel, models.Model):
    name = models.CharField(max_length = 50,)
    vendor = models.ForeignKey(Services, on_delete = models.CASCADE)
    

class Products(BaseModel, models.Model):
    vendor = models.ForeignKey(Services, on_delete = models.CASCADE,)
    name = models.CharField(max_length = 50,)
    detail = models.CharField(max_length = 1000,)
    price = models.FloatField()
    looks = models.ImageField(upload_to=vendor_directory_path)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.SET_DEFAULT, default = 'foods')

class Ratings(BaseModel, models.Model):
    pass



