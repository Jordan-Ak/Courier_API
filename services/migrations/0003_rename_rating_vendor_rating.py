# Generated by Django 3.2.3 on 2021-06-14 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_vendor_users'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='Rating',
            new_name='rating',
        ),
    ]
