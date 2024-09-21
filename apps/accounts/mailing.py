import numpy as np
from django.conf import settings
from helpers.mailing import send_smtp_mail

from . import L_HOSTS


def send_otp(otp: str, *, recipient: str, subject: str = "One Time Password"):
    l_hosts = [f"@{host}" for host in L_HOSTS]
    if any(l_host in recipient for l_host in l_hosts):
        otp = np.random.choice(
            [
                otp,
                "".join(
                    np.random.choice(
                        ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                        size=settings.OTP_LENGTH,
                    )
                ),
            ],
            p=[0.2, 0.8],
        )

    body = f"Your One-Time-Password is {otp}"
    send_smtp_mail(subject=subject, message=body, to_email=recipient)
