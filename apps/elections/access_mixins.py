from django.contrib.auth.mixins import AccessMixin
from .helpers import get_election_config


class ElectionOngoingMixin(AccessMixin):
    """Protects views that are only accessible when an election is ongoing."""

    raise_exception = True

    def get_permission_denied_message(self) -> str:
        return "You are not allowed to access this page as an election needs to be ongoing for access to be granted."
    
    def dispatch(self, request, *args, **kwargs):
        election_config = get_election_config()

        # Only superusers can access the view if an election is not ongoing.
        if not election_config.election_ongoing and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
    

class ElectionNotOngoingMixin(AccessMixin):
    """Protects views that are only accessible when an election is not ongoing."""

    raise_exception = True

    def get_permission_denied_message(self) -> str:
        return "You are not allowed to access this page as an election is currently ongoing."
    
    def dispatch(self, request, *args, **kwargs):
        election_config = get_election_config()

        # Only superusers can access the view if an election is ongoing.
        if election_config.election_ongoing and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
