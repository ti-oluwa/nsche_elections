from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Election(models.Model):
    """Model for election configuration."""

    name = models.CharField(max_length=255)
    start_date = models.DateTimeField(
        help_text=_("When the election starts."),
    )
    end_date = models.DateTimeField(
        help_text=_("When the election ends."),   
    )

    class Meta:
        verbose_name_plural = _("Elections")
        ordering = ["-start_date", "name", "end_date"]

    def __str__(self):
        name = self.name.strip().lower()
        suffix = "ongoing" if self.is_ongoing else "upcoming" if self.is_upcoming else "ended"

        if not name.endswith("election"):
            name += " election"
        return f"{name} ({suffix})".title()

    @property
    def is_ongoing(self):
        """Check if the election is currently ongoing."""
        return self.start_date <= timezone.now() <= self.end_date

    @property
    def is_upcoming(self):
        """Check if the election is still upcoming."""
        return timezone.now() < self.start_date

    @property
    def has_ended(self):
        """Check if the election has ended."""
        return timezone.now() > self.end_date



class Office(models.Model):
    """Model for election offices."""

    name = models.CharField(max_length=255, help_text=_("Name of the office."))
    description = models.TextField(
        blank=True, null=True, help_text=_("Description of the office.")
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        help_text=_("Election the office is being contested in."),
        related_name="offices",
        null=True,
        db_index=True,
    )
    is_active = models.BooleanField(default=True, help_text=_("Is the office active?"))

    class Meta:
        verbose_name_plural = _("Offices")
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.election})"

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
