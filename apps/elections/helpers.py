from .models import ElectionConfig


def get_election_config() -> ElectionConfig:
    """Returns election configuration object."""
    return ElectionConfig.objects.get_or_create()[0]
