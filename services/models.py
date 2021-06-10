from django.db import models
from common.models import BaseModel
from django.utils.translation import ugettext_lazy as _

# Create your models here.

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/vendor_<id>/<filename>
    return 'vendor_{0}/{1}'.format(instance.user.id, filename)

class Tag(BaseModel, models.Model):
    name = models.CharField(_('Tag Name'),max_length = 25,)

    def __str__(self):
        return self.name.title()

class Vendor(BaseModel, models.Model):
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

    name = models.CharField(_('Vendor Name'),max_length = 150,)
    service = models.CharField(_('Service'),max_length = 6, choices=service_choices)
    tags = models.ManyToManyField(Tag)
    opening_time = models.TimeField(_('Opening Time'), null = True)
    closing_time = models.TimeField(_('Closing Time'), null = True)
    location = models.CharField(_('location'),max_length = 200)
    cover = models.ImageField(_('Vendor image cover'),upload_to=vendor_directory_path)
    Rating = models.DecimalField(_('Rating'),decimal_places=1, editable=False, max_digits = 2, null = True)

    def __str__(self):
        return self.name.title()

class Location(BaseModel, models.Model):
    pass

class ProductCategory(BaseModel, models.Model):
    name = models.CharField(_('Product category name'),max_length = 50,)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE,)
    

class Products(BaseModel, models.Model):
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE,)
    name = models.CharField(_('Product Name'),max_length = 50,)
    detail = models.CharField(_('Product Detail'),max_length = 1000,)
    price = models.FloatField(_('Product Price'),)
    looks = models.ImageField(_('Product Image'),upload_to=vendor_directory_path)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.SET_DEFAULT, default = 'foods')

    def __str__(self):
        return self.name.title()

class Ratings(BaseModel, models.Model):
    pass



