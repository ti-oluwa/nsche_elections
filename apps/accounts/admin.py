from django.contrib import admin

from .models import UserAccount


@admin.register(UserAccount)
class UserAccountModelAdmin(admin.ModelAdmin):
    """Custom UserAccount model admin."""

    def save_model(self, request, obj, form, change):
        # If password is set, then set it using the set_password method
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data["password"])
        obj.save()
        return None
