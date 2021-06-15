from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from accounts.services import user_retrieve_pk
from django.utils.translation import ugettext_lazy as _
from .models import Schedule, Tag, Vendor


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


def vendor_get_name(name) -> Vendor:
    try:
        vendor = Vendor.objects.get(name = name)
    except Vendor.DoesNotExist:
        raise serializers.ValidationError(_('Vendor does not exist.'))
    return vendor
        

def vendor_get_id(id) -> Vendor:
    try:
        vendor = Vendor.objects.get(id = id)
    
    except (Vendor.DoesNotExist, ValidationError):
        raise serializers.ValidationError(_('Vendor does not exist.'))
    return vendor

def vendor_get_user(user) -> Vendor:
    try:
        vendor = Vendor.objects.get(user = user)
    except Vendor.DoesNotExist:
        raise serializers.ValidationError(_('This user has no associated Vendor'))

    return vendor        

def vendor_delete(object) -> None:
    object.delete()



def vendor_create(user,**kwargs) -> Vendor:
    
    for tag in kwargs.get('tags', ''):
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
    
    for tag in kwargs.get('tags', ''):
        tag_obj = tag_get_id(tag['id'])
        new_vendor.tags.add(tag_obj.id)   #Check this why add '.id'
    
    return new_vendor

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
    if schedule_duplicate_check:
        raise serializers.ValidationError(_('You have already created a Schedule for this day'))

    schedule = Schedule.objects.create(vendor =vendor, weekday = weekday,
                            from_hour = kwargs.get('from_hour',''),
                            to_hour = kwargs.get('to_hour',''),
                            )
      
    schedule.save()
    schedule.vendor_status()
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