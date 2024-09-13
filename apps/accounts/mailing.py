import typing
from django.conf import settings
from django.core.mail import EmailMessage


def send_mail(
    subject: str,
    body: str,
    recipients: typing.List[str],
    from_email: str = settings.DEFAULT_FROM_EMAIL,
    **kwargs,
) -> None:
    """
    Sends mails
    """
    kwargs.setdefault("reply_to", None)
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=f"{settings.APPLICATION_NAME} <{from_email}>",
        to=recipients,
        **kwargs,
    )

    email.send(fail_silently=False)
    return


def send_otp(otp: str, *, recipient: str, subject: str = "One Time Password"):
    body = f"Your OTP is {otp}"
    send_mail(subject=subject, body=body, recipients=[recipient])
