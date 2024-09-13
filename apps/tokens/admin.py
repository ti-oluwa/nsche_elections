from django.contrib import admin
from django.http import HttpRequest

from .models import UserRelatedTOTP, IdentifierRelatedTOTP


@admin.register(UserRelatedTOTP)
class UserRelatedTOTPModelAdmin(admin.ModelAdmin):
    """Model admin for the UserRelatedTOTP model"""

    list_display = ["owner", "validity_period", "requestor_ip_address", "created_at"]
    search_fields = [
        "owner__email",
        "owner__firstname",
        "owner__lastname",
        "requestor_ip_address",
        "created_at",
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False


@admin.register(IdentifierRelatedTOTP)
class IdentifierRelatedTOTPModelAdmin(admin.ModelAdmin):
    """Model admin for the IdentifierRelatedTOTP model"""

    list_display = [
        "identifier",
        "validity_period",
        "requestor_ip_address",
        "created_at",
    ]
    search_fields = ["identifier", "requestor_ip_address"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(self, request: HttpRequest, obj=None) -> bool:
        return False
