# Generated by Django 3.2.3 on 2021-06-15 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_alter_vendor_service'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='closed_open',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Closed'), (1, 'Open')], default=0, verbose_name='Closed or Open'),
        ),
    ]
