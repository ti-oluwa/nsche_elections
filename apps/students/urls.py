from django.urls import path

from . import views


app_name = "students"

urlpatterns = [
    path("", views.students_list_view, name="student_list"),
    path("new/", views.student_add_view, name="new_student"),
    path("import/", views.student_import_view, name="import_students"),
    path("delete/<uuid:student_id>/", views.student_delete_view, name="delete_student"),
]
