from __future__ import absolute_import, unicode_literals

# Create your tasks here

from celery import shared_task
from django.contrib.auth import get_user_model


@shared_task
def add(x, y):
    return x + y

@shared_task
def print_user(user_id):
    print(user_id)