from accounts.tasks import generate_token_sh
import secrets
import random
import string

from django.utils import timezone
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.managers import CustomUserManager
from common.models import BaseModel
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class CustomUser(AbstractUser, BaseModel):
  
    username = None
    date_joined = None
    email = models.EmailField(_('email address'), blank=False, unique = True)
    first_name = models.CharField(_('first name'), max_length=150, blank=False, null = True)
    last_name = models.CharField(_('last name'), max_length=150, blank=False, null = True)
    phone_no = PhoneNumberField(_('phone number'),unique = True,)
    
    is_verified_email = models.BooleanField(_('is verified email'), default = False)
    is_verified_phone = models.BooleanField(_('is verified phone'), default = False)
    on_news = models.BooleanField(_('on newsletter'), default = False)
    password_last_changed = models.DateTimeField(_('password last changed'), null = True)

    one_time_password = models.CharField(_('One time password'), null = True, max_length = 6)
    one_time_sent_at = models.DateTimeField(_('One time sent at'), null = True)
    email_verification_token = models.CharField(_('email token'), null = True, max_length =255)
    email_token_sent_at = models.DateTimeField(_('token sent at'), null = True)
    password_reset_token = models.CharField(_('Password reset token'), null = True, max_length =255)
    password_reset_sent_at = models.DateTimeField(_('Password reset sent at'), null = True)

    def generate_otp(self) -> None:
        numbers = string.digits
        self.one_time_password = ''.join(random.choice(numbers) for i in range(6))
        self.one_time_sent_at = timezone.now()
        self.save()

    def has_otp_expired(self) -> bool:
        return timezone.now() > self.one_time_sent_at + timedelta(hours = 0.2)
    
    def generate_token(self) -> str:
        token = secrets.token_urlsafe(50)
        return token

    def generate_email_verification_token(self) -> None:
        self.email_verification_token = generate_token_sh.apply_async().get()
        self.email_token_sent_at = timezone.now()
        self.save()

    def generate_password_verification_token(self) -> None:
        self.password_reset_token = generate_token_sh.apply_async().get()
        self.password_reset_sent_at = timezone.now()
        #self.password_last_changed = timezone.now()
        self.save()


    def has_email_verification_token_expired(self) -> bool:
        return timezone.now() > self.email_token_sent_at + timedelta(hours = 5)

    def has_password_reset_token_expired(self) -> bool:
        return timezone.now() > self.password_reset_sent_at + timedelta(hours = 5)

    def confirm_email(self) -> None:
        self.email_verification_token = None
        self.email_token_sent_at = None
        self.is_verified_email = True
        self.save()
    
    def confirm_reset(self) -> None:
        self.password_reset_token = None
        self.password_reset_sent_at = None
        self.password_last_changed = timezone.now()
        self.save()

    def confirm_phone(self) -> None:
        self.is_verified_phone = True
        self.one_time_password = None
        self.one_time_sent_at = None

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name','phone_no']

    def __str__(self) -> str:
        return self.email
