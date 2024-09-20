from django.db import models
from django.utils import timezone


class ElectionQuerySet(models.QuerySet):
    def ongoing(self):
        now = timezone.now()
        return self.filter(start_date__lte=now, end_date__gte=now)

    def upcoming(self):
        now = timezone.now()
        return self.filter(start_date__gt=now)

    def ended(self):
        now = timezone.now()
        return self.filter(end_date__lt=now)

    def with_counts(self):
        return self.annotate(
            offices_count=models.Count("offices", distinct=True),
            candidates_count=models.Count(
                "offices__candidates",
                filter=models.Q(offices__candidates__disqualified=False),
                distinct=True,
            ),
        )


class ElectionManager(models.Manager.from_queryset(ElectionQuerySet)):
    pass


class CandidateQuerySet(models.QuerySet):
    def qualified(self):
        return self.filter(disqualified=False)

    def disqualified(self):
        return self.filter(disqualified=True)

    def with_votes_count(self):
        return self.annotate(
            votes_count=models.Count(
                "votes", filter=models.Q(votes__is_valid=True), distinct=True
            )
        )

    def ordered_by_votes_count(self):
        return self.with_votes_count().order_by("-votes_count")


class CandidateManager(models.Manager.from_queryset(CandidateQuerySet)):
    pass


class OfficeQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def with_leading_candidate(self):
        from .models import Candidate

        # Subquery to get the leading candidate for the offices
        # in the queryset, if any
        return self.annotate(
            leading_candidate=models.Subquery(
                Candidate.objects.filter(
                    office=models.OuterRef("pk"), disqualified=False
                )
                .with_votes_count()
                .order_by("-votes_count")
                .values("name")[:1]
            )
        )

    def with_candidates_count(self):
        return self.annotate(
            candidates_count=models.Count(
                "candidates",
                filter=models.Q(candidates__disqualified=False),
                distinct=True,
            )
        )


class OfficeManager(models.Manager.from_queryset(OfficeQuerySet)):
    pass


class VoteQuerySet(models.QuerySet):
    def valid(self):
        return self.filter(is_valid=True)

    def invalid(self):
        return self.filter(is_valid=False)


class VoteManager(models.Manager.from_queryset(VoteQuerySet)):
    pass
