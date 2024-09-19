from django import forms
from django.conf import settings
from timezone_field.forms import TimeZoneFormField

from apps.students.forms import validate_matriculation_number


def validate_password(password: str) -> None:
    """Validate password"""
    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters long")
    if not any(char.isdigit() for char in password):
        raise forms.ValidationError("Password must contain at least one digit")
    if not any(char.isupper() for char in password):
        raise forms.ValidationError(
            "Password must contain at least one uppercase letter"
        )
    if not any(char.islower() for char in password):
        raise forms.ValidationError(
            "Password must contain at least one lowercase letter"
        )
    if not any(char in "!@#$%^&*()-_+=[]{}|;:,.<>?/" for char in password):
        raise forms.ValidationError(
            "Password must contain at least one special character"
        )
    return None


class SignInForm(forms.Form):
    """Form for user sign in"""

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    matriculation_number = forms.CharField(
        max_length=16, required=False, validators=[validate_matriculation_number]
    )

    def clean_matriculation_number(self) -> str:
        matriculation_number: str = self.cleaned_data.get("matriculation_number")
        if matriculation_number:
            return matriculation_number.upper()
        return matriculation_number


class StudentDetailVerificationForm(forms.Form):
    """Form for verifying student detail"""

    email = forms.EmailField(required=True)
    matriculation_number = forms.CharField(
        max_length=16, required=True, validators=[validate_matriculation_number]
    )

    def clean_matriculation_number(self) -> str:
        matriculation_number: str = self.cleaned_data["matriculation_number"]
        return matriculation_number.upper()
    

class OTPVerificationForm(forms.Form):
    """Form for verifying registration OTP"""

    otp = forms.CharField(required=True, max_length=settings.OTP_LENGTH)
    email = forms.EmailField(required=True)
    matriculation_number = forms.CharField(
        max_length=16, required=True, validators=[validate_matriculation_number]
    )

    def clean_matriculation_number(self) -> str:
        matriculation_number: str = self.cleaned_data["matriculation_number"]
        return matriculation_number.upper()


class RegistrationCompletionForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True, validators=[validate_password])
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_set_token = forms.CharField(required=True, widget=forms.HiddenInput)
    timezone = TimeZoneFormField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError({"confirm_password": "Passwords do not match."})

        return cleaned_data


