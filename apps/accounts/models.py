import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from timezone_field.fields import TimeZoneField

from .managers import UserAccountManager


class AccountType(models.TextChoices):
    STUDENT = "student", _("Student")
    ADMIN = "admin", _("Admin")


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """Model representing a user account"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    account_type = models.CharField(
        max_length=120, choices=AccountType.choices, default=AccountType.STUDENT
    )
    email = models.EmailField(unique=True)
    timezone = TimeZoneField(default="UTC", blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("User account")
        verbose_name_plural = _("User accounts")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.get_username()
