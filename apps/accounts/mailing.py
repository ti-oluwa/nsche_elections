from helpers.mailing import send_smtp_mail


def send_otp(otp: str, *, recipient: str, subject: str = "One Time Password"):
    body = f"Your One-Time-Password is {otp}"
    send_smtp_mail(subject=subject, message=body, to_email=recipient)
