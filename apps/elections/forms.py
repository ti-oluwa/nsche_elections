from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Election, Office, Candidate, Vote


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
                raise forms.ValidationError(
                    _("The start date must be earlier than the end date.")
                )

            if start_date < timezone.now():
                raise forms.ValidationError(_("The start date cannot be in the past."))

        return cleaned_data


class OfficeForm(forms.ModelForm):
    """Form for creating and updating offices."""

    class Meta:
        model = Office
        fields = ["name", "description", "election", "is_active"]

    def clean_election(self):
        election = self.cleaned_data.get("election")

        if election.has_ended:
            raise forms.ValidationError(
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
            raise forms.ValidationError(
                _("You cannot assign a candidate to an ended election's office.")
            )
        return office


class VoteForm(forms.ModelForm):
    """Form for registering votes."""

    class Meta:
        model = Vote
        fields = ["candidate", "voter"]
    
    def clean(self):
        cleaned_data = super().clean()
        candidate: Candidate = cleaned_data.get("candidate")
        voter = cleaned_data.get("voter")

        if candidate.office.election.has_ended:
            raise forms.ValidationError(_("You cannot vote in an ended election."))

        if Vote.objects.filter(candidate=candidate, voter=voter).exists():
            raise forms.ValidationError(
                _(f"You have already registered a vote for {candidate.name}.")
            )

        return cleaned_data
    
    def save(self, commit: bool = True):
        candidate = self.cleaned_data["candidate"]
        voter = self.cleaned_data["voter"]

        existing_vote_for_office = Vote.objects.filter(
            candidate__office=candidate.office, voter=voter
        ).first()
        if existing_vote_for_office:
            existing_vote_for_office.candidate = candidate
            vote = existing_vote_for_office
        else:
            vote = super().save(commit=False)

        if commit:
            vote.save()
        return vote
