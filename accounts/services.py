from django.contrib.auth import get_user_model
from rest_framework import serializers
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