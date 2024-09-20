from django.urls import path

from . import views


app_name = "elections"


urlpatterns = [
    path("", views.index_view, name="index"),
    path("elections/", views.election_list_view, name="election_list"),
    path("elections/<slug:slug>/", views.election_detail_view, name="election_detail"),
]
