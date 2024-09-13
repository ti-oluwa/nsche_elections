from typing import Any
from django.db import models
from django.http import HttpRequest

from helpers.requests import get_ip_address


class TimeBasedOTPManager(models.Manager):
    use_in_migrations = True

    def create(self, **kwargs: Any) -> Any:
        """Create time based OTP. Passing the request object auto-captures the requestor's IP address"""
        request: HttpRequest | None = kwargs.pop("request", None)
        if request:
            ip = get_ip_address(request).exploded
            kwargs["requestor_ip_address"] = ip
        return super().create(**kwargs)
