# Generated by Django 3.2.3 on 2021-06-16 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_auto_20210616_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='products',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Product Price'),
        ),
    ]
