# Generated by Django 3.2.3 on 2021-06-25 14:50

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0023_rename_location_userlocation_formatted_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlocation',
            name='coordinates',
            field=django.contrib.gis.db.models.fields.PointField(null=True, srid=4326),
        ),
    ]