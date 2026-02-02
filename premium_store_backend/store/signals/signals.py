from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import CustomUser
from ..models import Customer


@receiver(post_save, sender=CustomUser)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)