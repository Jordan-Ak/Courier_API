from django.db import models
from common.models import BaseModel

# Create your models here.


class Tags(BaseModel, models.Model):
    name = models.CharField(max_length = 25,)

    def __str__(self):
        return self.name

class Services(BaseModel, models.Model):
    RESTAURANT = 'REST'
    PARTY = 'PARTY'
    PHARMACY = 'PHAR'
    GROCERIES = 'GRO'
    CLOTHING = 'CLOTH'
    service_choices = [
        (RESTAURANT, 'restaurant'),
        (PARTY, 'party'),
        (PHARMACY, 'pharmacy'),
        (GROCERIES, 'groceries'),
        (CLOTHING, 'clothing'),
    ]
    name = models.CharField(max_length = 150,)
    service = models.CharField(max_length = 6, choices=service_choices)
    tags = models.ManyToManyField(Tags)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    location = models.CharField()

    def __str__(self):
        return self.name

class Location(BaseModel, models.Model):
    pass

class Products(BaseModel, models.Model):
    vendor = models.ForeignKey(Services, on_delete = models.CASCADE,)
    name = models.CharField(max_length = 50,)
    detail = models.CharField(max_length = 100,)
    price = models.FloatField()

class Ratings(BaseModel, models.Model):
    pass



