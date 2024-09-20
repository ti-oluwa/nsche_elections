from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.itercompat import is_iterable
from apps.students.models import Student


UserModel = get_user_model()


class StudentUserAuthenticationBackend(ModelBackend):
    """Custom authentication backend that aims to authenticate
    users (students) by email and matriculation number."""

    email_credentials = ("email", "username")
    matriculation_number_credentials = ("matriculation_number", "mat_no")

    def authenticate(self, request, **credentials):
        email = self.get_email(credentials)
        matriculation_number = self.get_matriculation_number(credentials)
        password = credentials.get("password", None)

        if not email or not password:
            return None

        if matriculation_number:
            return self.authenticate_student(email, matriculation_number, password)
        return self.authenticate_user(**credentials)

    def get_email(self, credentials):
        """Get the email from the credentials."""
        email_credentials = type(self).email_credentials

        if not is_iterable(email_credentials):
            email_credentials = [email_credentials]

        for credential_name in email_credentials:
            email = credentials.get(credential_name, None)
            if email:
                return email
        return None

    def get_matriculation_number(self, credentials):
        """Get the matriculation number from the credentials."""
        matriculation_number_credentials = type(self).matriculation_number_credentials

        if not is_iterable(matriculation_number_credentials):
            matriculation_number_credentials = [matriculation_number_credentials]

        for credential_name in matriculation_number_credentials:
            matriculation_number = credentials.get(credential_name, None)
            if matriculation_number:
                return matriculation_number
        return None

    def authenticate_student(
        self, email: str, matriculation_number: str, password: str
    ):
        """Authenticate a student by email and matriculation number."""
        try:
            student = Student.objects.get(
                email__iexact=email, matriculation_number__iexact=matriculation_number
            )
            account = student.account
            if account and account.check_password(password):
                return account
        
        except Student.DoesNotExist:
            return None
        return None

    def authenticate_user(self, **credentials):
        """Authenticate regular users by email."""
        email = self.get_email(credentials)
        password = credentials.get("password", None)

        try:
            user = UserModel.objects.get(email=email)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        return None
