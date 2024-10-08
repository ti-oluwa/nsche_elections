from django.contrib import admin
from django.http import HttpRequest

from .models import UserAccount


@admin.register(UserAccount)
class UserAccountModelAdmin(admin.ModelAdmin):
    """Custom UserAccount model admin."""

    # Adding search functionality
    search_fields = ['name', 'email', 'account_type']

    # Adding filter functionality
    list_filter = ['account_type', 'is_staff', 'is_superuser', 'is_active', 'timezone']

    def save_model(self, request, obj, form, change):
        # If password is set, then set it using the set_password method
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data["password"])
        obj.save()
        return None

    def has_module_permission(self, request: HttpRequest) -> bool:
        return request.user.is_superuser

