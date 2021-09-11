import googlemaps
import more_itertools
import re
from datetime import datetime, timedelta, timezone
from django.conf import settings
from django.contrib.gis.geos import Point
from collections import namedtuple
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from accounts.services import user_retrieve_pk
from django.utils.translation import ugettext_lazy as _
from .models import Checkout, CustomerCart, Location, ProductCategory, Product, Rating, Schedule, Tag, UserLocation, Vendor


def tag_create(name) -> object:
    tag = Tag.objects.create(name = name)
    tag.save()
    return tag

def tag_get_name(name):
    try:
        tag = Tag.objects.get(name = name)
    except Tag.does_not_exist:
            tag = None
    if not tag:
        raise serializers.ValidationError(_('Tag does not exist.'))
    return tag

def tag_get_id(id):
    try:
        tag = Tag.objects.get(id = id)
    except Tag.DoesNotExist:
        tag = None
    if not tag:
        raise serializers.ValidationError(_('Tag does not exist.'))
    return tag

def tag_delete(object):
    object.delete()


def vendor_get_name(name) -> Vendor: #fetch vendor object by name
    try:
        vendor = Vendor.objects.get(name = name)
    except Vendor.DoesNotExist:
        raise serializers.ValidationError(_('Vendor does not exist.'))
    return vendor
        

def vendor_get_id(id) -> Vendor: #Fetch vendor object by id
    try:
        vendor = Vendor.objects.get(id = id)
    
    except (Vendor.DoesNotExist, ValidationError):
        raise serializers.ValidationError(_('Vendor does not exist.'))
    return vendor

def vendor_get_user(user) -> Vendor: #Fetch vendor object by user
    try:
        vendor = Vendor.objects.get(users = user)
    except Vendor.DoesNotExist:
        raise serializers.ValidationError(_('This user has no associated Vendor'))

    return vendor        

def vendor_delete(object) -> None:
    object.delete()



def vendor_create(user,**kwargs) -> Vendor:
    
    for tag in kwargs.get('tags', ''): #Validation for if tag exists
        tag_id = tag_get_id(tag['id'])  
        if not tag_id:
            raise serializers.ValidationError(_('Tag does not exist.'))
    
    
    new_vendor = Vendor.objects.create(name = kwargs.get('name'), service = kwargs.get('service'), 
                                          cover = kwargs.get('cover',''),
                                          users = user,)
    new_vendor.save()
    
    for tag in kwargs.get('tags', ''): #code for adding tag, this is syntax code for many to many relation
        tag_obj = tag_get_id(tag['id'])
        new_vendor.tags.add(tag_obj.id)   #Check this why add '.id' done tick
    
    #Below code is for creating an appropriate Product category for the service
    product_name = None
    service = kwargs.get('service')
    if service == 'REST':
        product_cat_name = 'Foods and Drinks'
    if service == 'PARTY':
        product_cat_name = 'Alcohol and Chops'
    if service == 'PHAR':
        product_cat_name = 'Medication'
    if service == 'GRO':
        product_cat_name = 'Groceries'
    if service == 'CLOTH':
        product_cat_name = 'Clothing'
   
    product_cat = ProductCategory.objects.create(name = product_cat_name, vendor=new_vendor)
    product_cat.save()
    product_cat.generate_slug_name()
    
    return new_vendor

def vendor_retrieve_validation(vendor, user_id):
    if vendor.users.id != user_id:
        raise serializers.ValidationError(_('This user cannot retrieve this vendor.'))


def vendor_update(instance, **validated_data) -> Vendor:
    for tag in validated_data.get('tags', ''):
        tag_id = tag_get_id(tag['id'])  ###Validation if tags are correct.
        if not tag_id:
            raise serializers.ValidationError(_('Tag does not exist.'))

    new_tags = validated_data.get('tags', '') #Validation if there are new tags at all.
    
    if new_tags:
        for tag in instance.tags.all():
            instance.tags.remove(tag)    #Logic to remove all tags not passed newly

        for tag in new_tags:
            tag = tag_get_id(tag['id'])
            instance.tags.add(tag)     #Logic to add new tags
    #else:
        #for tag in instance.tags.all():
            #instance.tags.add(tag)
        
    instance.location = validated_data.get('location', instance.location)
    instance.cover = validated_data.get('cover', instance.cover)

    instance.save()

    return instance

def schedule_create(user_id,**kwargs):
    vendor = vendor_get_id(kwargs['vendor'])
    try:
        vendor_obj = Vendor.objects.filter(users = user_id).filter(id = vendor.id)
    except Vendor.DoesNotExist:
        raise serializers.ValidationError(_('This Vendor does not exist'))
    if not vendor_obj:
        raise serializers.ValidationError(_("This Vendor is unavailable to current user."))

    weekday = kwargs['weekday']
    schedule_duplicate_check = Schedule.objects.filter(vendor = vendor).filter(weekday =weekday)
    if schedule_duplicate_check: #Validation if the weekday already exists for this vendor
        raise serializers.ValidationError(_('You have already created a Schedule for this day'))

    schedule = Schedule.objects.create(vendor =vendor, weekday = weekday,
                            from_hour = kwargs.get('from_hour',''),
                            to_hour = kwargs.get('to_hour',''),
                            )
      
    schedule.save()
    schedule.vendor_status() #This code runs to save if vendors are closed or open for particular day
    return schedule

def schedule_update(instance,**validated_data):

    instance.from_hour = validated_data.get('from_hour', instance.from_hour)
    instance.to_hour = validated_data.get('to_hour', instance.to_hour)

    instance.save()
    instance.vendor_status()
    return instance

def schedule_vendor_day_filter(vendor, weekday):
    try:
        schedule = Schedule.objects.filter(vendor=vendor).filter(weekday = weekday)[0]
    except IndexError:
        raise serializers.ValidationError(_('Schedule for this day does not exist.'))
    return schedule

def schedule_vendor_filter(vendor):
    try:
        schedules = Schedule.objects.filter(vendor=vendor)
    except ValidationError:
        raise serializers.ValidationError(_('This vendor does not exist.'))
    return schedules    

def product_category_create(vendor,user_id, **kwargs):
    vendor_obj = vendor_get_id(vendor)
    if vendor_obj.users.id != user_id:
        raise serializers.ValidationError(_('This user cannot create category for this vendor')) #Validation only owner of vendor can create product category

    product_cat = ProductCategory.objects.create(name = kwargs.get('name', ''), vendor=vendor_obj)
    product_cat.save()
    product_cat.generate_slug_name()
    return product_cat

def product_category_update(instance,vendor, user_id,**kwargs):
    if not instance: #This means the instance didn't exist at a point in the flow
        raise serializers.ValidationError(_('This product category does not exist.'))
    
    vendor_obj = vendor_get_id(vendor)
    if vendor_obj.users.id != user_id: #Validation if user owns vendor
        raise serializers.ValidationError(_('This user cannot update this Vendor'))

    default_product_cat = ProductCategory.objects.filter(vendor = vendor).order_by('date_created')[0]
    
    if instance == default_product_cat: #This code is to protect default vendor categories made
        raise serializers.ValidationError(_('You cannot rename default categories'))

    instance.name = kwargs.get('name', instance.name)
    instance.save()
    instance.generate_slug_name()
    return instance

def product_category_delete(product_obj, user_id):
    vendor_user = product_obj.vendor.users
    vendor = product_obj.vendor.id
    if vendor_user.id != user_id:
        raise serializers.ValidationError(_('This user cannot make changes to this vendor'))
    
    default_product_cat = ProductCategory.objects.filter(vendor = vendor).order_by('date_created')[0]
    
    if product_obj == default_product_cat: #code to protect default categories created
        raise serializers.ValidationError(_('You cannot delete default categories'))

    product_obj.delete()

def product_category_ven_cat_filter(vendor, product_cat):
    try:
        object = ProductCategory.objects.filter(vendor = vendor).filter(slug_name = product_cat)
    except ValidationError: 
        return None
    if not object:
        return None
    else:
        product = object[0]
    return product

def product_category_ven_filter(vendor):
    object = ProductCategory.objects.filter(vendor = vendor)
    return object    

def product_category_get_id(id) -> ProductCategory:
    try:
        product_cat_object= ProductCategory.objects.get(id = id)
    except ProductCategory.DoesNotExist:
        raise serializers.ValidationError(_('This product category does not exist.'))
    return product_cat_object

def product_user_validation(vendor, user_id):
    vendor_obj = vendor_get_id(vendor)
    if vendor_obj.users.id != user_id:
        raise serializers.ValidationError(_('This user is not authorized to view this endpoint.'))
    

def product_get_id(id) -> Product:
    try:
        product_object= Product.objects.get(id = id)
    except Product.DoesNotExist:
        raise serializers.ValidationError(_('This product does not exist.'))
    return product_object

def product_create(vendor_obj, **kwargs):
    product_categories_obj = ProductCategory.objects.filter(vendor = vendor_obj.id)
    product_category_dict = kwargs['product_category']
    product_category_id = product_category_dict.get('id')
    product_cat_obj = product_category_get_id(product_category_id)
    
    if product_cat_obj not in product_categories_obj:
        raise serializers.ValidationError(_('This Category does not exist with current vendor.'))

    product = Product.objects.create(name = kwargs.get('name'), detail = kwargs.get('detail',''),
                           price = kwargs.get('price',''), looks = kwargs.get('looks',''),
                           product_category = product_cat_obj, vendor = vendor_obj)
                           
    product.save()
    product.generate_slug_name()
    return product

def product_update(instance, **kwargs):
    product_categories_obj = ProductCategory.objects.filter(vendor = instance.vendor.id)
    product_category_dict = kwargs.get('product_category', '')
    product_category_id = None
    product_cat_obj = None
    if product_category_dict:
        product_category_id = product_category_dict.get('id')
    #instance.product_category
    if product_category_id:
        product_cat_obj = product_category_get_id(product_category_id)

        if product_cat_obj not in product_categories_obj:
            raise serializers.ValidationError(_('This Category does not exist with current vendor.'))
    
    instance.name = kwargs.get('name', instance.name)
    instance.detail = kwargs.get('detail', instance.detail)
    instance.price = kwargs.get('price', instance.price)
    instance.looks = kwargs.get('looks', instance.looks)
    if product_cat_obj:
        instance.product_category = product_cat_obj

    instance.save()
    instance.generate_slug_name()
    return instance
    
def product_delete(object):
    object.delete()

    
def product_ven_pro_cat_slug_filter(vendor, product_cat, product_name):
    try:
        product_obj = Product.objects.filter(vendor = vendor).filter(
                                    product_category = product_cat).filter(slug_name = product_name)[0]
    except (IndexError, ValidationError):
        raise serializers.ValidationError(_('This product does not exist in this category or vendor'))
    
    return product_obj

def rating_exist(user, vendor):
    rating = Rating.objects.filter(who_rated = user).filter(vendor_rated = vendor)
    if rating:
        return rating


def rating_create(vendor, user_id, **kwargs):
    vendor_obj = vendor_get_id(vendor)
    user_obj = user_retrieve_pk(user_id)
    rating = kwargs.get('rating', '')
    if rating > 5 or rating < 0:
        raise serializers.ValidationError(_('Rating must be in range 0 - 5'))
    if vendor_obj.users.id == user_id:
        raise serializers.ValidationError(_('You cannot rate your own vendor.'))

    exist_rating = rating_exist(user_obj, vendor_obj)
    if exist_rating:
        rating_update(exist_rating[0], **kwargs)
    else:
        rating_obj = Rating.objects.create(vendor_rated = vendor_obj,
                                     who_rated = user_obj, rating = kwargs.get('rating',''))
    
        rating_obj.save()
        return rating_obj

def rating_update(instance, user, **kwargs):
    if not instance: #This means the instance didn't exist at a point in the flow
        raise serializers.ValidationError(_('This rating does not exist.'))
    if instance.who_rated != user or user.is_staff == False:
        raise serializers.ValidationError(_('This user cannot access this endpoint'))
    rating = kwargs.get('rating', instance.rating)
    if  rating> 5 or rating < 0:
        raise serializers.ValidationError(_('Rating must be in range 0 - 5'))
    
    instance.rating = rating
    instance.save()
    return instance

def rating_delete(object):
    object.delete()

def rating_get_id(rating_id):
    try:
        rating = Rating.objects.get(id = rating_id)
    
    except Rating.DoesNotExist:
        raise serializers.ValidationError(_('This object does not exist.'))
    
    return rating

def rating_user_validation(rating, user):
    if rating.who_rated.id != user.id or user.is_staff != True:
        raise serializers.ValidationError(_('This endpoint is unavailable to user'))

def customer_cart_get(user):
    exist_cart = CustomerCart.objects.filter(user = user, ordered = False)
    if exist_cart:
        return exist_cart[0]
    else:
        return None

def customer_cart_get_id(id):
    try:
       customer_cart =  CustomerCart.objects.get(id = id)
    except CustomerCart.DoesNotExist:
        raise serializers.ValidationError(_('Requested cart does not exist.'))
    return customer_cart    

def customer_cart_ordered_user_filter(user):
    products = CustomerCart.objects.filter(ordered = False).filter(user = user)
    return products

def cart_product_validation(user, **kwargs):
    #Code to add quantity to already added product.
    product_select = kwargs.get('product','')
    current_cart = CustomerCart.objects.filter(user = user).filter(ordered = False).filter(
                                                product = product_select['id'])
    if current_cart:
        cart = current_cart[0]
        cart.quantity += 1
        cart.save()
        cart.gen_total_price()
        return cart

def cart_user_validation(user, product):
    if user.is_staff or product.user == user:
        pass
    else:
        raise serializers.ValidationError(_('This user does not own this cart.'))
                 

def customer_cart_create(user, **kwargs):
    product_obj = kwargs.get('product','')
    product = product_get_id(product_obj['id'])
    vendor = product.vendor

    customer_cart = CustomerCart.objects.create(product = product, quantity = kwargs.get('quantity', 1),
                                                ordered = False, vendor = vendor, user = user)
    customer_cart.save()
    customer_cart.gen_total_price()
    return customer_cart

def customer_cart_update(instance, **kwargs):
    if not instance:
        raise serializers.ValidationError(_('This cart is empty.'))

    instance.quantity = kwargs.get('quantity', instance.quantity)
    instance.save()
    instance.gen_total_price()
    return instance

def customer_cart_delete(object):
    object.delete()



def location_get(**kwargs):
    gmaps = googlemaps.Client(key = settings.GOOGLE_API_KEY)
    input_location = kwargs.get('formatted_address', '')
    geocode_location = gmaps.geocode(input_location)
    formatted_address = geocode_location[0].get('formatted_address')
    if not formatted_address:
        raise serializers.ValidationError('This location is not recognized')

    coordinates_dict = (geocode_location[0].get('geometry').get('location'))
    lat = coordinates_dict.get('lat')
    lng = coordinates_dict.get('lng')
    coordinates = f'POINT({lat} {lng})'
    return_dictionary = {'formatted_address':formatted_address, 'coordinates':coordinates}
    return return_dictionary

def location_create(user, vendor, **location):
    #vendor = vendor_get_user(user)
    formatted_address = location.get('formatted_address', '')
    coordinates = location.get('coordinates', '')
    #I wonder if the created location saves I think it does without explicitly calling the save function.  
    Location.objects.create(vendor =vendor, formatted_address = formatted_address, coordinates = coordinates)
    vendor.address = formatted_address
    vendor.save()

def google_time_parser(date_string)-> datetime:
    parsed_date = None
    try:
        parsed_date = datetime.strptime(date_string, '%M mins')
        return parsed_date    
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hours %M mins')
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hours %M min' )
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hour %M mins')
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hour %M min')
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%M min')
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hours')
        return parsed_date
    except ValueError:
        pass
    try:
        parsed_date = datetime.strptime(date_string, '%H hour')
        return parsed_date
    except ValueError:
        pass

def parsed_time_total(parsed_dates):
    time_0 = '0 hours 0 mins'  #Zero time implemented to convert datetime instances to timedelta when subtract
    total_time = timedelta(seconds = 0, microseconds= 0, milliseconds= 0)
    parsed_0 = google_time_parser(time_0)
    for date in parsed_dates:
        
        format_time = date - parsed_0
        total_time += format_time
        #print(total_time, format_time)
    return(total_time)

def formatted_time_total(delta_time):
    seconds = delta_time.seconds
    hours = seconds//3600
    minutes = (seconds//60)%60
    return(f'{hours} hours {minutes} minutes')

def transit_get(location_list) -> dict:
    gmaps = googlemaps.Client(key = settings.GOOGLE_API_KEY)
    locations = location_list
    distance = 0
    parsed_dates = []
    for a,b in more_itertools.pairwise(locations):
        result = gmaps.distance_matrix(a, b)
        distance_result = result['rows'][0]['elements'][0]['distance']['text']
        duration_result = result['rows'][0]['elements'][0]['duration']['text']
        
        distance_list = re.findall(r"[-+]?\d*\.\d+|\d+", distance_result) #Regex expressions to extract value from string
        distance += (float(distance_list[0]))
        
        parsed_date = google_time_parser(duration_result)
        parsed_dates.append(parsed_date)
    
    final_parsed_time = parsed_time_total(parsed_dates)
    final_formatted_time = formatted_time_total(final_parsed_time)
    return({'distance': f'{distance} km', 'final_formatted_time': final_formatted_time,
            'final_parsed_time': final_parsed_time})

def user_location_get_user(user):
    try:
        user_location = UserLocation.objects.get(user = user)
    except UserLocation.DoesNotExist:
        raise serializers.ValidationError(_('No location is associated with this user'))
    return user_location

def user_location_create(user, **formatted_address):
    location = formatted_address.get('formatted_address', '')
    coordinates = formatted_address.get('coordinates', '')
    user_location = UserLocation.objects.create(user = user, formatted_address = location,
                                                coordinates = coordinates)
    user_location.save()
    return user_location
  

def user_location_validation(user, **formatted_address):
    queryset = UserLocation.objects.filter(user = user)
    if queryset:
        update =  user_location_update(queryset[0], **formatted_address)
        return update
    else:
        return None

def user_location_update(instance, **formatted_address):
    instance.formatted_address = formatted_address.get('formatted_address', instance.formatted_address)
    instance.coordinates = formatted_address.get('coordinates', instance.coordinates)
    instance.save()
    return instance

    

def checkout_cart(user):
    checkout_cart = customer_cart_ordered_user_filter(user)
    return checkout_cart
    
def final_price_calculate(query_dict): #This object is not a dictionary instead a list of objects
    final_price = 0
    for product in query_dict: #Iterating through a list of objects using key totalprice
        final_price += product.total_price
    return final_price

def compile_locations(cart, user_location_obj):
    locations = []
    for product in cart:
        vendor_id = product.vendor.id
        vendor = vendor_get_id(vendor_id)
        locations.append(vendor.address)
    set_locations = set(locations) #Set method makes locations unique, only one drawback in unique use case
    list_locations = list(set_locations)
    list_locations.append(user_location_obj.formatted_address)
    return list_locations


def checkout_temp_create(final_price, user, user_location,**transit_dict):
    checkout_obj = Checkout.objects.create(final_price = final_price, 
                            transit_time = transit_dict['final_formatted_time'],
                            transit_distance = transit_dict['distance'], location = user_location,
                             user = user)
    checkout_obj.delete() #That is why the "temp" is there because it is a temporary object that gets deleted.
    return checkout_obj

def checkout_create(final_price, user, user_location,**transit_dict):
    checkout_obj = Checkout.objects.create(final_price = final_price, 
                            transit_time = transit_dict['final_formatted_time'],
                            transit_distance = transit_dict['distance'], location = user_location,
                             user = user)
    
    return checkout_obj

def cart_ordered_true(cart):
    for product in cart:
        product.ordered = True
        product.ordered_time = datetime.now()
        product.save()




