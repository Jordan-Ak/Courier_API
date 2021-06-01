from accounts.tasks import user_email_verification_flow_sh
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.views import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


def validate_password(password) -> str:
    min_length = 7

    if len(password) < min_length:
        raise serializers.ValidationError(_(f'Your password must be at least {min_length} characters'))
    
    elif not any(char.isdigit() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one number.'))
    
    elif not any(char.isalpha() for char in password):
        raise serializers.ValidationError(_('Your password must contain at least one letter.'))

    return password


def user_email_verified_check(user) -> None:
    if user.is_verified_email:
        raise serializers.ValidationError(_('Your email is already verified'))

def user_email_verification_flow(user_email, user_token) -> None:    
    mail_message = 'This is your email verification link'
    send_mail(
        'Email Verification at Courier Services',
         f'{mail_message}  http://127.0.0.1:8000/accounts/verify_mail/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)



def user_create(email, first_name, last_name, phone_no, password) -> get_user_model:
    user: get_user_model = get_user_model().objects.create(email=email, first_name = first_name,
                                    last_name = last_name, phone_no = phone_no)

    user.set_password(password)

    user.save()
    
    user.generate_email_verification_token()
    user_email_verification_flow_sh.delay(user.email, user.email_verification_token)
    return user

def user_email_verification_confirm(user):
    if user.has_email_verification_token_expired():
        raise serializers.ValidationError(_('Resend email verification this token has expired'))
    
    elif user.is_verified_email:
        raise serializers.ValidationError(_('User is already verified'))
   
    else:
        user.confirm_email()



def user_retrieve_pk(id) -> get_user_model:
    user = get_object_or_404(get_user_model(),id = id)
    return user



def user_retrieve_em(email) -> get_user_model:
    user = get_object_or_404(get_user_model(),email = email)
    return user

def user_retrieve_pass_tk(token) -> get_user_model:
    user = get_object_or_404(get_user_model(), password_reset_token = token)
    return user

def user_update(instance, **validated_data):
    instance.first_name = validated_data.get('first_name', instance.first_name)
    instance.last_name = validated_data.get('last_name', instance.last_name)
    instance.on_news = validated_data.get('on_news', instance.on_news)

    instance.save()
    return instance

def user_password_change(user, **serializer_data):
    if not user.check_password(serializer_data['old_password']):
        raise serializers.ValidationError(_('Old password is incorrect.'))
    
    user.set_password(serializer_data['password'])
    user.password_last_changed = timezone.now()
    user.save()

def user_password_reset_send(user_email, user_token):
    mail_message = 'This is your Password reset link'
    send_mail(
        'Password Reset at Courier Services',
         f'{mail_message}  http://127.0.0.1:8000/accounts/password/reset/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)

def user_password_reset_validation(user):
    if user.has_password_reset_token_expired():
        raise serializers.ValidationError(_('Reset Password again this link has expired'))

def user_password_reset_change(user, new_password):
    if user.has_password_reset_token_expired():
        raise serializers.ValidationError(_('Reset Password again this link has expired'))
    
    user.confirm_reset()
    user.set_password(new_password)
    user.save()



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