from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from payments.models import UserBalance


@receiver(post_save, sender=User)
def create_balance(sender, instance, created, **kwargs):
    if created:
        UserBalance.objects.create(user=instance)
