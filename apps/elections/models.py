from django.db import models
from django.utils.translation import gettext_lazy as _

from django.utils import timezone


class ElectionConfig(models.Model):
    """Model for election configuration."""

    election_starts = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("When is the next election scheduled to start?"),
    )
    election_ends = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Election Configuration"

    @property
    def election_ongoing(self):
        """Check if an election is currently ongoing."""
        if self.election_starts is None or self.election_ends is None:
            return False
        return self.election_starts <= timezone.now() <= self.election_ends

    @property
    def election_upcoming(self):
        """Check if an election is upcoming."""
        if self.election_starts is None:
            return False
        return timezone.now() < self.election_starts

    @property
    def election_ended(self):
        """Check if an election has ended."""
        if self.election_ends is None:
            return False
        return timezone.now() > self.election_ends


class Office(models.Model):
    """Model for election offices."""

    name = models.CharField(max_length=255, help_text=_("Name of the office."))
    description = models.TextField(
        blank=True, null=True, help_text=_("Description of the office.")
    )
    is_active = models.BooleanField(default=True, help_text=_("Is the office active?"))

    class Meta:
        verbose_name_plural = _("Offices")
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def leading_candidate(self):
        """Return the candidate with the most valid votes for the office."""
        leading_candidate = (
            Candidate.objects.filter(office=self, disqualified=False)
            .annotate(
                votes_count=models.Count("votes", filter=models.Q(votes__is_valid=True))
            )
            .order_by("-votes_count")
            .first()
        )
        return leading_candidate


class Candidate(models.Model):
    """Model for election candidates."""

    name = models.CharField(max_length=255, help_text=_("Name of the candidate."))
    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        help_text=_("Office the candidate is contesting for."),
        related_name="candidates",
    )
    manifesto = models.TextField(
        blank=True, null=True, help_text=_("Manifesto of the candidate.")
    )
    disqualified = models.BooleanField(
        default=False, help_text=_("Is the candidate disqualified?")
    )

    class Meta:
        verbose_name_plural = _("Candidates")
        ordering = ("name",)

    def __str__(self):
        return self.name

    @property
    def votes_count(self):
        """Return the number of valid votes the candidate has received."""
        return Vote.objects.filter(candidate=self, is_valid=True).count()


class Vote(models.Model):
    """Model for election votes."""

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        help_text=_("Candidate the vote is for."),
        related_name="votes",
        db_index=True,
    )
    voter = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        help_text=_("Voter that cast the vote."),
        related_name="+",
    )
    is_valid = models.BooleanField(default=True, help_text=_("Is the vote valid?"))

    class Meta:
        verbose_name_plural = _("Votes")
        # Ensures a voter can only vote for a candidate once
        unique_together = ("candidate", "voter")

    def __str__(self):
        return f"{self.voter} voted for {self.candidate}"
