# Generated by Django 3.2.3 on 2021-06-16 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0009_alter_products_price'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Products',
            new_name='Product',
        ),
    ]