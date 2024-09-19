from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin


class IndexView(LoginRequiredMixin, generic.TemplateView):
    """View for the index page."""

    template_name = "elections/index.html"


index_view = IndexView.as_view()
