from django.db import models
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Election


election_qs = Election.objects.prefetch_related("offices__candidates").all()


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """View for the index page."""

    template_name = "elections/index.html"


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



index_view = IndexView.as_view()
election_list_view = ElectionListView.as_view()
election_detail_view = ElectionDetailView.as_view()
