from services.models import ProductCategory
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from .models import ProductCategory, Product


@receiver(pre_delete, sender = ProductCategory,)#Signal for reassigning foreign key after cat deletion
def set_products_to_default_product_category(sender, instance, **kwargs):
    
    products = Product.objects.filter(product_category = instance.id)
    default_category = ProductCategory.objects.filter(vendor = instance.vendor.id).order_by('date_created')[0]
  
    for product in products:
        product.product_category = default_category
        product.save()