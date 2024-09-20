import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone, text

from .managers import ElectionManager, CandidateManager, OfficeManager, VoteManager

class Election(models.Model):
    """Model for election configuration."""

    slug = models.SlugField(
        unique=True,
        help_text=_("Unique identifier for the election. Used in URLs."),
        editable=False,
    )
    name = models.CharField(max_length=255)
    description = models.TextField(
        blank=True, null=True, help_text=_("Description of the election.")
    )
    start_date = models.DateTimeField(
        help_text=_("When the election starts."),
    )
    end_date = models.DateTimeField(
        help_text=_("When the election ends."),   
    )

    objects = ElectionManager()

    class Meta:
        verbose_name_plural = _("Elections")
        ordering = ["-start_date", "end_date", "name"]

    def __str__(self):
        name = self.name.strip().lower()
        suffix = "ongoing" if self.is_ongoing else "upcoming" if self.is_upcoming else "ended"

        if "election" not in name:
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
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = get_slug_from_name(self.name)

            while Election.objects.filter(slug=slug).exists():
                slug = get_slug_from_name(self.name)
            self.slug = slug
            
        super().save(*args, **kwargs)


def get_slug_from_name(name):
    """Generate a unique slug from the given name."""
    slug = text.slugify(name)
    return f"{slug}-{uuid.uuid4().hex[:8]}"


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

    objects = OfficeManager()

    class Meta:
        verbose_name_plural = _("Offices")
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.election})"


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

    objects = CandidateManager()

    class Meta:
        verbose_name_plural = _("Candidates")
        ordering = ("name",)

    def __str__(self):
        return self.name



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

    objects = VoteManager()

    class Meta:
        verbose_name_plural = _("Votes")
        # Ensures a voter can only vote for a candidate once
        unique_together = ("candidate", "voter")

    def __str__(self):
        return f"{self.voter} voted for {self.candidate}"
