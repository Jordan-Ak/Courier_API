from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.views import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


def validate_password(password) -> str:
    min_length = 7

    if len(password) < min_length:
        raise serializers.ValidationError(_(f'Your password must be at least {min_length} characters'))
    
    elif not any(char.isdigit() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one number.'))
    
    elif not any(char.isalpha() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one letter.'))

    return password

def user_create(email, first_name, last_name, phone_no, password) -> get_user_model:
    user: get_user_model = get_user_model().objects.create(email=email, first_name = first_name,
                                    last_name = last_name, phone_no = phone_no)

    user.set_password(password)

    user.save()
    return user

def user_retrieve_pk(id) -> get_user_model:
    user = get_object_or_404(get_user_model(),id = id)
    return user



def user_retrieve_em(email) -> get_user_model:
    user = get_object_or_404(get_user_model(),email = email)
    return user

def user_update(instance, **validated_data):
    instance.first_name = validated_data.get('first_name', instance.first_name)
    instance.last_name = validated_data.get('last_name', instance.last_name)
    instance.on_news = validated_data.get('on_news', instance.on_news)

    instance.save()
    return instance

def user_delete(instance)-> None:
    instance.delete()

    """
    Code that enables admins to keep user details after account deletion 
    if instance.first_name:
        instance.first_name = None
        instance.last_name = None
        instance.is_active = False
        instance.save()
    else:
        return Response({'message':'User already deleted'}, status= status.HTTP_400_BAD_REQUEST)
    """