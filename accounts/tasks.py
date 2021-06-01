from __future__ import absolute_import, unicode_literals

# Create your tasks here

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
#from accounts.services import user_email_verification_flow


@shared_task
def add(x, y):
    return x + y

@shared_task
def print_user(user_id):
    print(user_id)

@shared_task
def user_email_verification_flow_sh(user_email, user_token):
    mail_message = 'This is your email verification link'
    send_mail(
        'Email Verification at Courier Services',
         f'{mail_message}  http://127.0.0.1:8000/accounts/verify_mail/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)

@shared_task
def user_password_reset_send_sh(user_email, user_token):
    mail_message = 'This is your Password reset link'
    send_mail(
        'Password Reset at Courier Services',
         f'{mail_message}  http://127.0.0.1:8000/accounts/password/reset/confirm/{user_token}',
        'from admin@email.com',
        [f'{user_email}'],
        fail_silently = False,)