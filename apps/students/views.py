from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Student
from apps.accounts.access_mixins import AdminOnlyMixin

students_queryset = Student.objects.all()


class StudentListView(AdminOnlyMixin, LoginRequiredMixin, generic.ListView):
    """View for displaying a list of students."""

    queryset = students_queryset
    template_name = "students/student_list.html"
    context_object_name = "students"


students_list_view = StudentListView.as_view()
