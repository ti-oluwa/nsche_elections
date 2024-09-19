from django.db.models import F, BooleanField, ExpressionWrapper
from django.utils import timezone
from .models import Election


def get_ongoing_elections(prefetch_related: bool = True):
    now = timezone.now()

    # Annotate the ongoing status
    elections = Election.objects.annotate(
        is_ongoing=ExpressionWrapper(
            (F("start_date") <= now) & (F("end_date") >= now),
            output_field=BooleanField(),
        )
    ).filter(is_ongoing=True)

    # Conditionally apply prefetch_related
    if prefetch_related:
        elections = elections.prefetch_related(
            "offices__candidates"  # Prefetch related offices and candidates
        )

    return elections


def get_upcoming_elections(prefetch_related: bool = True):
    now = timezone.now()

    # Annotate the upcoming status
    elections = Election.objects.annotate(
        is_upcoming=ExpressionWrapper(
            F("start_date") > now, output_field=BooleanField()
        )
    ).filter(is_upcoming=True)

    # Conditionally apply prefetch_related
    if prefetch_related:
        elections = elections.prefetch_related(
            "offices__candidates"  # Prefetch related offices and candidates
        )

    return elections


def get_ended_elections(prefetch_related: bool = True):
    now = timezone.now()

    # Annotate the ended status
    elections = Election.objects.annotate(
        has_ended=ExpressionWrapper(F("end_date") < now, output_field=BooleanField())
    ).filter(has_ended=True)

    # Conditionally apply prefetch_related
    if prefetch_related:
        elections = elections.prefetch_related(
            "offices__candidates"  # Prefetch related offices and candidates
        )

    return elections
