import typing
import json
import os
from django.db import transaction
from django.views import generic
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from helpers.exceptions import capture
from .models import Student, AcademicLevel
from .forms import StudentForm
from .students_upload import import_students_from_file
from apps.accounts.access_mixins import AdminOnlyMixin
from apps.elections.access_mixins import ElectionNotOngoingMixin

students_qs = Student.objects.all()


class StudentListView(AdminOnlyMixin, LoginRequiredMixin, generic.ListView):
    """View for displaying a list of students."""

    queryset = students_qs
    template_name = "students/student_list.html"
    context_object_name = "students"

    def get_context_data(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context_data = super().get_context_data(**kwargs)
        context_data["academic_levels"] = {
            level.name.replace("_", " ").strip(): level.value for level in AcademicLevel
        }
        return context_data


@capture.enable
@capture.capture(content="Oops! An error occurred while record the given details.")
class StudentAddView(
    ElectionNotOngoingMixin, AdminOnlyMixin, LoginRequiredMixin, generic.View
):
    """View for add a new student"""

    http_method_names = ["post"]
    form_class = StudentForm

    def post(self, request, *args, **kwargs):
        data: typing.Dict = json.loads(request.body)
        form = self.form_class(data=data)

        if not form.is_valid():
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "An error occurred",
                    "errors": form.errors,
                },
                status=400,
            )

        student = form.save()
        return JsonResponse(
            data={
                "status": "success",
                "detail": f"Details for {student} were recorded!",
                "redirect_url": reverse("students:student_list"),
            },
            status=200,
        )


@capture.capture(content="Oops! An error occurred while importing the given details.")
@capture.enable
class StudentImportView(
    ElectionNotOngoingMixin, AdminOnlyMixin, LoginRequiredMixin, generic.View
):
    """View for adding students in bulk using details contained in an uploaded file of defined format"""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        students_file = request.FILES.get("students_file")

        if not students_file:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "`students_file` is required",
                },
                status=400,
            )

        _, ext = os.path.splitext(students_file.name)
        if ext.lower() != ".csv":
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Only CSV files are allowed",
                },
                status=400,
            )

        with capture.capture(ValueError, code=400):
            students = import_students_from_file(students_file)

        return JsonResponse(
            data={
                "status": "success",
                "detail": f"{len(students)} new students were found and imported!",
                "redirect_url": reverse("students:student_list"),
            },
            status=200,
        )


class StudentDeleteView(
    ElectionNotOngoingMixin, AdminOnlyMixin, LoginRequiredMixin, generic.View
):
    """View for deleting a student"""

    queryset = students_qs
    http_method_names = ["get"]

    def get_object(self):
        return get_object_or_404(self.queryset, id=self.kwargs["student_id"])

    def get(self, request, *args, **kwargs):
        student = self.get_object()
        
        with transaction.atomic():
            student.delete()
            if student.account:
                student.account.delete()
        return redirect(self.get_success_url())

    def get_success_url(self) -> str:
        return reverse("students:student_list")


students_list_view = StudentListView.as_view()
student_add_view = StudentAddView.as_view()
student_import_view = StudentImportView.as_view()
student_delete_view = StudentDeleteView.as_view()
