from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Election, Office, Candidate
from django.utils.translation import gettext_lazy as _


class ElectionForm(forms.ModelForm):
    """Form for creating and updating elections."""

    class Meta:
        model = Election
        fields = ["name", "description", "start_date", "end_date"]
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date >= end_date:
                raise ValidationError(
                    _("The start date must be earlier than the end date.")
                )

            if start_date < timezone.now():
                raise ValidationError(_("The start date cannot be in the past."))

        return cleaned_data


class OfficeForm(forms.ModelForm):
    """Form for creating and updating offices."""

    class Meta:
        model = Office
        fields = ["name", "description", "election", "is_active"]

    def clean_election(self):
        election = self.cleaned_data.get("election")

        if election.has_ended:
            raise ValidationError(
                _("You cannot assign an office to an ended election.")
            )
        return election


class CandidateForm(forms.ModelForm):
    """Form for creating and updating candidates."""

    class Meta:
        model = Candidate
        fields = ["name", "office", "manifesto", "disqualified"]

    def clean_office(self):
        office = self.cleaned_data.get("office")

        if office.election.has_ended:
            raise ValidationError(
                _("You cannot assign a candidate to an ended election's office.")
            )
        return office
