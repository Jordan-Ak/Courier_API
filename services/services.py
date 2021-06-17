from collections import namedtuple
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from accounts.services import user_retrieve_pk
from django.utils.translation import ugettext_lazy as _
from .models import ProductCategory, Product, Schedule, Tag, Vendor


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
        vendor = Vendor.objects.get(user = user)
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
                                          #opening_time = kwargs.get('opening_time', None),
                                          #closing_time = kwargs.get('closing_time',None),
                                          location = kwargs.get('location',''), 
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
