from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from .models import Tag, Vendor


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
    except Tag.does_not_exist:
        tag = None
    if not tag:
        raise serializers.ValidationError(_('Tag does not exist.'))
    return tag

def tag_delete(object):
    object.delete()


def vendor_get(name) -> Vendor:
    try:
        vendor = Vendor.objects.get(name = name)
    except Vendor.does_not_exist:
        vendor = None
    if vendor:
        return vendor
    else:
        raise serializers.ValidationError(_('Vendor does not exist.'))


def vendor_delete(object) -> None:
    object.delete()

def vendor_create(**kwargs) -> Vendor:
    for tag in kwargs.get('tags', ''):
        tag_id = tag_get_id(tag['id'])  
        if not tag_id:
            raise serializers.ValidationError(_('Tag does not exist.'))
    new_vendor = Vendor.objects.create(name = kwargs.get('name'), service = kwargs.get('service'),
                                          opening_time = kwargs.get('opening_time', None),
                                          closing_time = kwargs.get('closing_time',None),
                                          location = kwargs.get('location',''), 
                                          cover = kwargs.get('cover',''))
    new_vendor.save()
    
    for tag in kwargs.get('tags', ''):
        tag_obj = tag_get_id(tag['id'])
        new_vendor.tags.add(tag_obj.id)
    
    return new_vendor

    