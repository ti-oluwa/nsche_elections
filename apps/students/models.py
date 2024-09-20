import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class AcademicLevel(models.TextChoices):
    """Model representing academic levels."""
    
    _100_LEVEL = "100", _("100 Level")
    _200_LEVEL = "200", _("200 Level")
    _300_LEVEL = "300", _("300 Level")
    _400_LEVEL = "400", _("400 Level")
    _500_LEVEL = "500", _("500 Level")
    _600_LEVEL = "600", _("600 Level")
    _700_LEVEL = "700", _("700 Level")


class Student(models.Model):
    """Model representing a student."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    level = models.CharField(max_length=120, choices=AcademicLevel.choices)
    department = models.CharField(max_length=120, default="Chemical Engineering", blank=True)
    matriculation_number = models.CharField(max_length=120, unique=True)
    email = models.EmailField(unique=True)
    account = models.OneToOneField(
        "accounts.UserAccount", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+"
    )

    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "email", "-level", "-added_at"]
        verbose_name = _("Student")
        verbose_name_plural = _("Students")
        unique_together = ["email", "matriculation_number"]

    def __str__(self) -> str:
        return f"{self.name} ({self.matriculation_number})"
