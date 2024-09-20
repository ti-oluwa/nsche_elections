from django.contrib.auth.mixins import AccessMixin

from .models import Election


class ElectionOngoingMixin(AccessMixin):
    """Protects views that are only accessible when an election is ongoing."""

    raise_exception = True

    def get_permission_denied_message(self) -> str:
        return "You are not allowed to access this page as an election needs to be ongoing for access to be granted."

    def dispatch(self, request, *args, **kwargs):
        ongoing_elections = Election.objects.only("pk").ongoing()
        # Check if there's at least one ongoing election
        if not ongoing_elections.exists() and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ElectionNotOngoingMixin(AccessMixin):
    """Protects views that are only accessible when an election is not ongoing."""

    raise_exception = True

    def get_permission_denied_message(self) -> str:
        return "You are not allowed to access this page as an election is currently ongoing."

    def dispatch(self, request, *args, **kwargs):
        # Check if there are any ongoing elections
        ongoing_elections = Election.objects.only("pk").ongoing()
        if ongoing_elections.exists() and not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
