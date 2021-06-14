from django.contrib import admin
from .models import Tag, Vendor
# Register your models here.
"""
    Created Admin Site to test something interesting.
    Just checking how the front-end componenet would integrate what's happening

"""


class TagAdmin(admin.ModelAdmin):
    model = Tag

class VendorAdmin(admin.ModelAdmin):
    model = Vendor
    readonly_fields = ('users',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Vendor, VendorAdmin)