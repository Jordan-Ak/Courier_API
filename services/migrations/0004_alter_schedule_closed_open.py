# Generated by Django 3.2.3 on 2021-06-14 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_rename_rating_vendor_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='closed_open',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Closed'), (1, 'Open')], null=True, verbose_name='Closed or Open'),
        ),
    ]
