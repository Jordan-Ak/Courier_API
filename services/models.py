import datetime
from datetime import timezone
from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.db.models.deletion import DO_NOTHING
from common.models import BaseModel
from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify


# Create your models here.

def vendor_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/vendor_<name>_<id>/<filename>
    return 'vendor_{0}_{1}/{2}'.format(instance.name, instance.id, filename)

def product_directory_path(instance, filename):
    #file will be uploaded to MEDIA_ROOT/vendor_<name>_<id>/product_cat/product
    return 'vendor_{0}_{1}/{2}/{3}'.format(instance.vendor.name, instance.vendor.id,
                                     instance.product_category.name,filename)

class Tag(BaseModel, models.Model):
    name = models.CharField(_('Tag Name'),max_length = 25,)

    def __str__(self):
        return self.name.title()

class Vendor(BaseModel, models.Model):
  #  RESTAURANT = 'REST'
   # PARTY = 'PARTY'
   # PHARMACY = 'PHAR'
   # GROCERIES = 'GRO'
   # CLOTHING = 'CLOTH'
   # service_choices = [
   #     (RESTAURANT, 'restaurant'),
   #     (PARTY, 'party'),
   #     (PHARMACY, 'pharmacy'),
    #    (GROCERIES, 'groceries'),
    #    (CLOTHING, 'clothing'),
    #]

    class ServiceChoices(models.TextChoices):
        RESTAURANT = 'REST', _('Restaurant')
        PARTY = 'PARTY', _('Party')
        PHARMACY = 'PHAR', _('Pharmacy')
        GROCERIES = 'GRO', _('Groceries')
        CLOTHING = 'CLOTH', _('Clothing')

    name = models.CharField(_('Vendor Name'),max_length = 150,)
    service = models.CharField(_('Service'),max_length = 6, choices=ServiceChoices.choices,)
    tags = models.ManyToManyField(Tag)
    #opening_time = models.TimeField(_('Opening Time'), null = True)
    #closing_time = models.TimeField(_('Closing Time'), null = True)
    location = models.CharField(_('location'),max_length = 200,)
    cover = models.ImageField(_('Vendor image cover'),upload_to=vendor_directory_path)
    rating = models.DecimalField(_('Rating'),decimal_places=1, editable=False, max_digits = 2, null = True)
    users = models.ForeignKey(get_user_model(), on_delete = models.SET_DEFAULT, default = '143d24de-78b8-478a-919b-1022059cc2ec')

    def gen_average_vendor_rating(self):
        rating_queryset = Rating.objects.filter(vendor_rated = self.id)
        if not rating_queryset:
            return None
        average_rating = rating_queryset.aggregate(average_rating=Avg('rating'))
        self.rating =  average_rating['average_rating']
        self.save()

    def __str__(self):
        return self.name.title()

class Schedule(BaseModel, models.Model):
    #WEEKDAYS = [
    #(0, _("Monday")),
    #(1, _("Tuesday")),
    #(2, _("Wednesday")),
    #(3, _("Thursday")),
    #(4, _("Friday")),
    #(5, _("Saturday")),
    #(6, _("Sunday")),
    #]
    class WeekdayChoices(models.IntegerChoices):
        MONDAY = 0, _('Monday')
        TUESDAY = 1, _('Tuesday')
        WEDNESDAY = 2, _('Wednesday')
        THURSDAY = 3, _('Thursday')
        FRIDAY = 4, _('Friday')
        SATURDAY = 5, _('Saturday')
        SUNDAY = 6, _('Sunday')
    
    class StatusChoices(models.IntegerChoices):
        CLOSED = 0, _('Closed')
        OPEN = 1, _('Open')


    #STATUS =[(0, _("Closed")), (1, _('Open')),]

    weekday = models.PositiveSmallIntegerField(_('Weekday'),choices = WeekdayChoices.choices)
    from_hour = models.TimeField(_('From Time'),)
    to_hour = models.TimeField(_('To Time'),)
    closed_open = models.PositiveSmallIntegerField(_('Closed or Open'),
                                                choices = StatusChoices.choices,default = 0) #CLOSED
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    
    class Meta:
        unique_together = ('vendor', 'weekday')

    def vendor_status(self):
        day_of_week = datetime.datetime.today().weekday()
        today_object = Schedule.objects.filter(vendor = self.vendor).filter(weekday = day_of_week)
        #Above code should return only one value
        try:
            today = today_object[0]
        except IndexError:
            return None      #This means weekday hasn't been set for this day
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
        
        today.save()

    def __str__(self):
        return f'{self.vendor.name.title()}, {self.weekday}'

class Location(BaseModel, models.Model):
    pass

class ProductCategory(BaseModel, models.Model):
    name = models.CharField(_('Product category name'),max_length = 50,)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE,)
    slug_name = models.SlugField(null = True, db_index=False)
    #method set_products_to_default_category lies in signals

    def generate_slug_name(self):
        self.slug_name = slugify(self.name)
        self.save()
    
#def products_category_set(self):
 #   return ProductCategory.objects.filter(vendor = self.vendor).order_by('date_created')[0]

class Product(BaseModel, models.Model):
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE,)
    name = models.CharField(_('Product Name'),max_length = 50,)
    detail = models.CharField(_('Product Detail'),max_length = 1000, null = True)
    price = models.DecimalField(_('Product Price'),max_digits=10, decimal_places=2,)
    looks = models.ImageField(_('Product Image'),upload_to=product_directory_path, null = True)
    product_category = models.ForeignKey(ProductCategory, on_delete=DO_NOTHING, null = True)
    slug_name = models.SlugField(null = True, db_index = False)

    def generate_slug_name(self):
        self.slug_name = slugify(self.name)
        self.save()

    def __str__(self):
        return self.name.title()

class Rating(BaseModel, models.Model):
    vendor_rated = models.ForeignKey(Vendor, on_delete = models.CASCADE, related_name = 'user_rating')
    who_rated = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators = [MaxValueValidator(5)])

    class Meta: #This constraint restricts users to have only one rating per book
        unique_together = ('who_rated', 'vendor_rated',)
    
    def __str__(self):
        return self.vendor_rated.name.title() + ', ' + self.who_rated.email


class CustomerCart(BaseModel, models.Model):
    #products = models.ManyToManyField(CustomerOrder)
    ordered = models.BooleanField(default = False)
    ordered_time = models.TimeField(null = True)
    delivered_time = models.TimeField(null = True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null = True)
    user = models.ForeignKey(get_user_model(), on_delete = models.CASCADE,)

    def gen_final_price(self):
        final_price = 0
        for product in self.customerorder_set.all():
            final_price += product.get_total_price()
        self.fianl_price = final_price
        self.save()

    def __str__(self):
        return f'{self.user}, {self.date_created}'

class CustomerOrder(BaseModel, models.Model):
    product = models.ForeignKey(Product, on_delete = DO_NOTHING)
    quantity = models.IntegerField(default = 1)
    ordered = models.BooleanField(default = False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null = True)
    user = models.ForeignKey(get_user_model(), on_delete = models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete = models.CASCADE)
    cart = models.ForeignKey(CustomerCart, on_delete = models.CASCADE)

    def gen_total_price(self):
        self.total_price = self.product.price * self.quantity
        self.save()
    
    def __str__(self):
        return f'{self.product.name}, {self.user}'