from django.urls import path

from . import views


app_name = "students"

urlpatterns = [
    path("", views.students_list_view, name="students_list"),
]
