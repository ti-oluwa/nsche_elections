from django.dispatch import receiver
from django.db.models.signals import post_migrate

from .models import ElectionConfig


@receiver(post_migrate)
def create_election_config_if_not_exists(sender, **kwargs):
    if ElectionConfig.objects.exists():
        return
    ElectionConfig.objects.create()
