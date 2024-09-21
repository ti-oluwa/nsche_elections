import json
import typing
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Candidate, Election, Office, VoteLock, Vote
from .forms import VoteForm
from helpers.exceptions import capture


election_qs = Election.objects.prefetch_related("offices__candidates").all()


class IndexView(LoginRequiredMixin, generic.RedirectView):
    """View for the index page."""

    def get_redirect_url(self, *args, **kwargs) -> str:
        return reverse("elections:election_list")


class ElectionListView(LoginRequiredMixin, generic.ListView):
    """View for listing elections."""

    template_name = "elections/election_list.html"
    queryset = election_qs
    context_object_name = "elections"

    def get_queryset(self) -> models.QuerySet[Election]:
        qs = super().get_queryset()
        status = self.request.GET.get("status", "all").lower()

        if status == "ongoing":
            return qs.ongoing()
        elif status == "upcoming":
            return qs.upcoming()
        return qs


class ElectionDetailView(LoginRequiredMixin, generic.DetailView):
    """View for election details."""

    template_name = "elections/election_detail.html"
    queryset = election_qs
    context_object_name = "election"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class VotingView(LoginRequiredMixin, generic.TemplateView):
    template_name = "elections/voting.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["election"] = get_object_or_404(election_qs, slug=self.kwargs["slug"])
        context["vote_locked"] = VoteLock.objects.filter(
            election=context["election"], voter=self.request.user
        ).exists()
        return context


@capture.enable
@capture.capture(content="Oops! An error occurred while registering your vote.")
class VoteRegistrationView(LoginRequiredMixin, generic.View):
    """View for registering votes."""

    http_method_names = ["post"]
    form_class = VoteForm

    def get_object(self) -> Office:
        election = get_object_or_404(election_qs, slug=self.kwargs["slug"])
        office = get_object_or_404(
            election.offices.prefetch_related("candidates"), pk=self.kwargs["office_id"]
        )
        return office

    def post(self, request, *args, **kwargs):
        # Prevent admin from participating in voting exercises
        if request.user.is_admin:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "You are not allowed to vote as an admin.",
                },
                status=400,
            )

        data: typing.Dict = json.loads(request.body)
        voter = self.request.user
        office = self.get_object()
        candidate_pk: str = data.get("candidate")

        if candidate_pk.lower() in ["null", "undefined", "nil", "none"]:
            # If the user has already voted, remove the vote for the office
            votes = Vote.objects.filter(voter=voter, candidate__office=office)
            if votes.exists():
                votes.delete()
                return JsonResponse(
                    data={
                        "status": "success",
                        "detail": f"Your vote for {office.name.upper()} has been withdrawn!",
                    },
                    status=200,
                )

            # If the user has not voted, return an error
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": "Your response has been recorded.",
                },
                status=200,
            )

        candidate: Candidate = get_object_or_404(office.candidates, pk=candidate_pk)
        form = self.form_class(data={"candidate": candidate, "voter": voter})

        if not form.is_valid():
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "An error occurred",
                    "errors": form.errors,
                },
                status=400,
            )

        form.save()
        return JsonResponse(
            data={
                "status": "success",
                "detail": f"You voted {candidate.name.title()} for {office.name.upper()}!",
            },
            status=200,
        )


class VoteLockInView(LoginRequiredMixin, generic.View):
    http_method_names = ["get"]

    def get_object(self) -> Election:
        return get_object_or_404(election_qs, slug=self.kwargs["slug"])

    def get(self, request, *args, **kwargs):
        # Prevent admin from participating in voting exercises
        if request.user.is_admin:
            return redirect("elections:voting", slug=self.kwargs["slug"])

        election = self.get_object()
        voter = self.request.user

        if not VoteLock.objects.filter(election=election, voter=voter).exists():
            VoteLock.objects.create(election=election, voter=voter)

        return redirect("elections:voting", slug=election.slug)


index_view = IndexView.as_view()
election_list_view = ElectionListView.as_view()
election_detail_view = ElectionDetailView.as_view()
voting_view = VotingView.as_view()
vote_registration_view = VoteRegistrationView.as_view()
vote_lock_in_view = VoteLockInView.as_view()
