from django import forms
from django.utils import timezone

from .models import ElectionConfig


class ElectionConfigForm(forms.ModelForm):
    """ModelForm for ElectionConfig model."""

    class Meta:
        model = ElectionConfig
        fields = "__all__"
        widgets = {
            "election_starts": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "election_ends": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

        def clean_election_starts(self):
            election_starts = self.cleaned_data.get("election_starts")
            if election_starts is None:
                return election_starts
            
            if election_starts < timezone.now():
                raise forms.ValidationError(
                    "Election cannot be scheduled to start in the past."
                )
            return election_starts

        def clean_election_ends(self):
            election_ends = self.cleaned_data.get("election_ends")
            if election_ends is None:
                return election_ends
            
            if election_ends < timezone.now():
                raise forms.ValidationError(
                    "Election cannot be scheduled to end in the past."
                )
            return election_ends

        def clean(self):
            cleaned_data = super().clean()
            election_starts = cleaned_data.get("election_starts")
            election_ends = cleaned_data.get("election_ends")

            if not election_starts or not election_ends:
                return cleaned_data

            if election_starts >= election_ends:
                raise forms.ValidationError(
                    "Election cannot be scheduled to start after it the scheduled end period."
                )
            return cleaned_data
