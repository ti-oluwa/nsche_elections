from django.http import HttpRequest
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django_otp.oath import TOTP
from django_otp.util import random_hex
import time
import base64

from . import managers
from helpers.requests import get_ip_address


class TimeBasedOTP(models.Model):
    """Base Time based OTP model"""

    key = models.CharField(max_length=50, default=random_hex, unique=True)
    last_verified_counter = models.IntegerField(default=-1)
    validity_period = models.IntegerField(default=settings.OTP_VALIDITY_PERIOD)
    length = models.IntegerField(default=settings.OTP_LENGTH)
    requestor_ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = managers.TimeBasedOTPManager()

    class Meta:
        abstract = True
        verbose_name = _("Time Based OTP")
        verbose_name_plural = _("Time Based OTPs")
        ordering = ["-created_at"]

    def totp(self) -> TOTP:
        """Constructs and returns a `django_otp.oath.TOTP` representation of the instance"""
        totp = TOTP(
            key=base64.b64encode(self.key.encode()),
            step=self.validity_period,
            digits=self.length,
        )
        # the current time will be used to generate a counter
        totp.time = time.time()
        return totp

    def token(self) -> str:
        """The OTP token"""
        totp = self.totp()
        token = str(totp.token()).zfill(self.length)
        return token

    def verify_token(
        self, token: str, *, request: HttpRequest = None, tolerance: int = 0
    ) -> bool:
        try:
            token = int(token)
        except ValueError:
            return False

        ip_address = get_ip_address(request).exploded if request else None
        # Ensure that the same device/machine that
        # requested the token's creation is the one verifying
        if (ip_address and self.requestor_ip_address) and (
            ip_address != self.requestor_ip_address
        ):
            return False

        totp = self.totp()
        # check if the current counter value is higher than the value of
        # last verified counter and check if entered token is correct by
        # calling totp.verify_token()
        if (totp.t() > self.last_verified_counter) and totp.verify(
            token, tolerance=tolerance
        ):
            # if the condition is true, set the last verified counter value
            # to current counter value, and return True
            self.last_verified_counter = totp.t()
            return True
        # if the token entered was invalid or if the counter value
        # was less than last verified counter, then return False
        return False


class UserRelatedTOTP(TimeBasedOTP):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="totp"
    )

    class Meta:
        verbose_name = _("User Related Time Based OTP")
        verbose_name_plural = _("User Related Time Based OTPs")
        ordering = ["-created_at"]


class IdentifierRelatedTOTP(TimeBasedOTP):
    identifier = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Identifier Related Time Based OTP")
        verbose_name_plural = _("Identifier Related Time Based OTPs")
        ordering = ["-created_at"]
