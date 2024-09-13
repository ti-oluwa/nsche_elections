from typing import Any, Hashable, Mapping, Union, Optional
from django.conf import settings
from django.http import HttpRequest
import random
from django.contrib.auth.models import AbstractBaseUser

from .models import IdentifierRelatedTOTP, UserRelatedTOTP
from helpers.identifiers import random_hex


def get_totp_by_identifier(identifier: str) -> IdentifierRelatedTOTP | None:
    try:
        totp = IdentifierRelatedTOTP.objects.filter(identifier=identifier).first()
    except IdentifierRelatedTOTP.DoesNotExist:
        return None
    return totp


def get_totp_by_owner(owner: AbstractBaseUser) -> UserRelatedTOTP | None:
    try:
        totp = UserRelatedTOTP.objects.filter(owner=owner).first()
    except UserRelatedTOTP.DoesNotExist:
        return None
    return totp


def generate_totp_for_identifier(
    identifier: str,
    *,
    length: int = settings.OTP_LENGTH,
    validity_period: int = settings.OTP_VALIDITY_PERIOD,
    request: Optional[HttpRequest] = None,
) -> IdentifierRelatedTOTP:
    existing_totp = get_totp_by_identifier(identifier)
    if existing_totp:
        existing_totp.delete()
    
    totp = IdentifierRelatedTOTP.objects.create(
        identifier=identifier,
        length=length,
        validity_period=validity_period,
        request=request,
    )
    return totp


def verify_identifier_totp_token(
    token: str,
    identifier: str,
    *,
    request: Optional[HttpRequest] = None,
    delete_on_verification: bool = True,
) -> bool:
    """
    Verify the Time based OTP token for the identifier.

    :param token: The token to verify.
    :param identifier: The identifier for which the token is to be verified.
    :param delete_on_verification: Whether to delete once verified.
    :return: True if the token is verified, False otherwise.
    """
    totp = get_totp_by_identifier(identifier)
    if not totp:
        return False

    if totp.verify_token(token, request=request):
        if delete_on_verification:
            totp.delete()
        return True
    return False


def generate_totp_for_user(
    user: AbstractBaseUser,
    *,
    length: int = settings.OTP_LENGTH,
    validity_period: int = settings.OTP_VALIDITY_PERIOD,
    request: Optional[HttpRequest] = None,
) -> UserRelatedTOTP:
    """
    Generate an Time based OTP for the user.

    :param user: The user for which the OTP is to be generated.
    :return: The OTP token generated
    """
    existing_totp = get_totp_by_owner(user)
    if existing_totp:
        existing_totp.delete()
    totp = UserRelatedTOTP.objects.create(
        owner=user, length=length, validity_period=validity_period, request=request
    )
    return totp


def verify_user_totp_token(
    token: str,
    user: AbstractBaseUser,
    *,
    request: Optional[HttpRequest] = None,
    delete_on_verification: bool = True,
) -> bool:
    """
    Verify the Time based OTP token for the user.

    :param token: The token to verify.
    :param user: The user for which the token is to be verified.
    :param delete_on_verification: Whether to delete once verified.
    :return: True if the token is verified, False otherwise.
    """
    totp = get_totp_by_owner(user)
    if not totp:
        return False

    if totp.verify_token(token, request=request):
        if delete_on_verification:
            totp.delete()
        return True
    return False


def verify_totp_token(
    token: str,
    on_behalf_of: Union[AbstractBaseUser, str, Any],
    *,
    request: Optional[HttpRequest] = None,
    delete_on_verification: bool = True,
) -> bool:
    if isinstance(on_behalf_of, AbstractBaseUser):
        return verify_user_totp_token(
            token,
            on_behalf_of,
            request=request,
            delete_on_verification=delete_on_verification,
        )
    return verify_identifier_totp_token(
        token,
        on_behalf_of,
        request=request,
        delete_on_verification=delete_on_verification,
    )


def dummy_verify_totp_token(**kwargs) -> bool:
    """Dummy version of the `verify_totp_token` function"""
    token = kwargs.get("token")
    return token == ("0" * settings.OTP_LENGTH)


def exchange_data_for_token(
    data: Mapping[Hashable, Any],
    *,
    expires_after: int = 5 * 60,
    request: Optional[HttpRequest] = None,
) -> str:
    identifier = random_hex(length=16)
    totp_length = random.randint(6, 12)
    totp = generate_totp_for_identifier(
        identifier, length=totp_length, validity_period=expires_after, request=request
    )
    totp.metadata = data
    totp.save()
    return ".".join((identifier, totp.token(), totp.key))


class InvalidToken(ValueError):
    pass


def exchange_token_for_data(
    access_token: str,
    *,
    request: Optional[HttpRequest] = None,
    delete_on_success: bool = True,
) -> Mapping[Hashable, Any] | None:
    try:
        identifier, token, _ = access_token.split(".")
    except ValueError:
        raise InvalidToken("Invalid access token")

    valid = verify_identifier_totp_token(
        token, identifier, request=request, delete_on_verification=False
    )
    if not valid:
        raise InvalidToken("Invalid access token")
    totp = IdentifierRelatedTOTP.objects.get(identifier=identifier)
    data = totp.metadata
    if delete_on_success:
        totp.delete()
    return data
