from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from .models import Tags, Services


def tag_create(name) -> object:
    tag = Tags.objects.create(name = name)
    tag.save()
    return tag

def tag_get_name(name):
    try:
        tag = Tags.objects.get(name = name)
    except Tags.does_not_exist:
            tag = None
    if not tag:
        raise serializers.ValidationError(_('Tag does not exist.'))
    return tag

def tag_get_id(id):
    try:
        tag = Tags.objects.get(id = id)
    except Tags.does_not_exist:
        tag = None
    if not tag:
        raise serializers.ValidationError(_('Tag does not exist.'))
    return tag

def tag_delete(object):
    object.delete()


def service_get(name) -> Services:
    try:
        service = Services.objects.get(name = name)
    except Services.does_not_exist:
        service = None
    if service:
        return service
    else:
        raise serializers.ValidationError(_('Vendor does not exist.'))


def service_delete(object) -> None:
    object.delete()

def service_create(**kwargs) -> Services:
    for tag in kwargs.get('tags', ''):
        tag_id = tag_get_id(tag['id'])  
        if not tag_id:
            raise serializers.ValidationError(_('Tag does not exist.'))
    new_service = Services.objects.create(name = kwargs.get('name'), service = kwargs.get('service'),
                                          opening_time = kwargs.get('opening_time', None),
                                          closing_time = kwargs.get('closing_time',None),
                                          location = kwargs.get('location',''), 
                                          cover = kwargs.get('cover',''))
    new_service.save()
    
    for tag in kwargs.get('tags', ''):
        tag_obj = tag_get_id(tag['id'])
        new_service.tags.add(tag_obj.id)
    
    return new_service

    