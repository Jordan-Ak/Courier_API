# Generated by Django 3.2.3 on 2021-06-25 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0022_auto_20210625_1340'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userlocation',
            old_name='location',
            new_name='formatted_address',
        ),
    ]
