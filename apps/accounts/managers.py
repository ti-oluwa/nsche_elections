from django.contrib.auth.models import BaseUserManager


class UserAccountManager(BaseUserManager):
    """Custom manager for `UserAccount` model."""

    use_in_migrations = True

    def create_user(self, email, password, save: bool = True, **extra_fields):
        if not email:
            raise ValueError("User must have an email!")
        if not password:
            raise ValueError("User must have a Password!")

        user = self.model(email=self.normalize_email(email=email), **extra_fields)

        user.set_password(password)
        if save is True:
            user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email, password=password, save=False, **extra_fields
        )
        user.account_type = "admin"
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.account_type = "admin"
        user.save(using=self._db)
        return user
