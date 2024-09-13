from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentModelAdmin(admin.ModelAdmin):
    """Admin class for the Student model."""
    list_display = ["name", "level", "department", "matriculation_number", "email"]
    list_filter = ["level", "department"]
    search_fields = ["name", "matriculation_number", "email"]
    readonly_fields = ["id", "added_at", "updated_at"]
    fieldsets = (
        (None, {
            "fields": ("id", "name", "level", "department", "matriculation_number", "email")
        }),
        ("Account", {
            "fields": ("account",)
        }),
        ("Timestamps", {
            "fields": ("added_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    ordering = ["name", "email", "-added_at"]
    actions = ["send_email_to_students"]

    def has_change_permission(self, request, obj=None):
        # Disable the ability to change the student's details
        return False
    
    def get_matriculation_number(self, obj: Student) -> str:
        return obj.matriculation_number.upper()

    def send_email_to_students(self, request, queryset):
        """Send an email to the selected students."""
        selected_students = queryset.values_list("name", "email")
        for student in selected_students:
            name, email = student
            # Send email to the student
            print(f"Sending email to {name} at {email}")
        self.message_user(request, "Email sent successfully.")
    
    send_email_to_students.short_description = "Send email to selected students"
