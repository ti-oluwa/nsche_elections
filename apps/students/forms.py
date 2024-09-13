import re
from django import forms

from .models import Student


MATRICULATION_NUMBER_PATTERN = re.compile(r"^[a-zA-Z]{3,4}\/\d{4,7}\/\d{4}$")


def validate_matriculation_number(matriculation_number: str) -> None:
    """Validate matriculation number"""
    if not MATRICULATION_NUMBER_PATTERN.match(matriculation_number):
        raise forms.ValidationError(
            "Invalid matriculation number. It should be in the format: ABC/123456/2024"
        )
    return None


class StudentForm(forms.ModelForm):
    """Form for creating students."""

    class Meta:
        model = Student
        fields = ("name", "level", "department", "matriculation_number", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["level"].widget.attrs.update({"class": "form-select"})

    def clean_matriculation_number(self) -> str:
        matriculation_number: str = self.cleaned_data["matriculation_number"]
        validate_matriculation_number(matriculation_number)
        return matriculation_number.upper()

