import datetime
from datetime import timezone
from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from django.utils.translation import ugettext_lazy as _

# Create your models here.

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/vendor_<name>_<id>/<filename>
    return 'vendor_{0}_{1}/{2}'.format(instance.name, instance.id, filename)

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
    #opening_time = models.TimeField(_('Opening Time'), null = True)
    #closing_time = models.TimeField(_('Closing Time'), null = True)
    location = models.CharField(_('location'),max_length = 200,)
    cover = models.ImageField(_('Vendor image cover'),upload_to=vendor_directory_path)
    rating = models.DecimalField(_('Rating'),decimal_places=1, editable=False, max_digits = 2, null = True)
    users = models.ForeignKey(get_user_model(), on_delete = models.SET_DEFAULT, default = '143d24de-78b8-478a-919b-1022059cc2ec')

    def __str__(self):
        return self.name.title()

class Schedule(BaseModel, models.Model):
    WEEKDAYS = [
    (0, _("Monday")),
    (1, _("Tuesday")),
    (2, _("Wednesday")),
    (3, _("Thursday")),
    (4, _("Friday")),
    (5, _("Saturday")),
    (6, _("Sunday")),
    ]
    
    STATUS =[(0, _("Closed")), (1, _('Open')),]

    weekday = models.PositiveSmallIntegerField(_('Weekday'),choices = WEEKDAYS)
    from_hour = models.TimeField(_('From Time'),)
    to_hour = models.TimeField(_('To Time'),)
    closed_open = models.PositiveSmallIntegerField(_('Closed or Open'), choices = STATUS,)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    
    class Meta:
        unique_together = ('vendor', 'weekday')

    def vendor_status(self):
        day_of_week = datetime.datetime.today().weekday()
        today_object = Schedule.objects.filter(vendor = self.vendor).filter(weekday = day_of_week)
        #Above code should return only one value
        today = today_object[0]
        current_time = datetime.datetime.now().time()
        
        """
        The below conditional statements determine Whether a store is open or closed on a certain day
        based on the logic below:
        if a day's opening time is greater than the closing time or vice-versa
        """
        if today.to_hour > today.from_hour:
            if current_time < today.from_hour:
                today.closed_open = 0 #Closed
        
            elif current_time > today.from_hour and current_time < today.to_hour:
                today.closed_open = 1 #Open

            elif current_time > today.to_hour:
                today.closed_open = 0 #Closed
        
        elif today.from_hour > today.to_hour:
            if current_time < today.to_hour:
                today.closed_open = 1 #Open
            
            elif current_time > today.to_hour and current_time < today.from_hour:
                today.closed_open = 0 #Closed

            elif current_time > today.from_hour:
                today.closed_open = 1 #Open
        
        self.save()

    def __str__(self):
        self.vendor.name.title()

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



