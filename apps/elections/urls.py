from django.urls import path

from . import views


app_name = "elections"


urlpatterns = [
    path("", views.index_view, name="index"),
    path("elections/", views.election_list_view, name="election_list"),
    path("elections/<slug:slug>/", views.election_detail_view, name="election_detail"),
    path("elections/<slug:slug>/vote/", views.voting_view, name="voting"),
    path(
        "elections/<slug:slug>/vote/<int:office_id>/",
        views.vote_registration_view,
        name="vote",
    ),
    path(
        "elections/<slug:slug>/lock-in-vote/",
        views.vote_lock_in_view,
        name="vote_lock_in",
    ),
]
