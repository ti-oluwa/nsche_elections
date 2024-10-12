import typing
import json
from urllib.parse import urlencode as urllib_urlencode
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.students.models import Student
from .models import UserAccount
from helpers.exceptions import capture
from helpers.response.decorators import redirect_authenticated
from helpers.requests import parse_query_params_from_request
from .forms import (
    SignInForm,
    StudentDetailVerificationForm,
    RegistrationOTPVerificationForm,
    RegistrationCompletionForm,
    PasswordResetInitiationForm,
    PasswordResetOTPVerificationForm,
    PasswordResetCompletionForm,
)
from .helpers import get_student, create_account_for_student
from .mailing import send_otp
from apps.tokens.totp import (
    InvalidToken,
    generate_totp_for_identifier,
    dummy_verify_totp_token,
    verify_identifier_totp_token,
    exchange_data_for_token,
    exchange_token_for_data,
)


class SignInView(generic.TemplateView):
    """View for user sign in"""

    template_name = "accounts/signin.html"
    form_class = SignInForm

    @redirect_authenticated("elections:election_list")
    def get(self, request, *args: str, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args: str, **kwargs) -> JsonResponse:
        """Handles user authentication AJAX/Fetch POST request"""
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

        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        mat_no = form.cleaned_data["matriculation_number"]
        user_account = authenticate(
            request, username=email, password=password, matriculation_number=mat_no
        )
        if user_account:
            login(request, user_account)

            query_params = parse_query_params_from_request(request)
            next_url = query_params.pop("next", None)
            if next_url and query_params:
                other_query_params = urllib_urlencode(query_params)
                next_url = f"{next_url}?{other_query_params}"
            return JsonResponse(
                data={
                    "status": "success",
                    "detail": f"Hello {user_account.name}!",
                    "redirect_url": next_url or reverse("elections:index"),
                },
                status=200,
            )

        return JsonResponse(
            data={"status": "error", "detail": "Invalid credentials!"}, status=400
        )


class SignOutView(LoginRequiredMixin, generic.View):
    """View for user sign out"""

    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("accounts:signin")


######################
# REGISTRATION VIEWS #
######################


@redirect_authenticated("elections:election_list")
class RegistrationView(generic.TemplateView):
    template_name = "accounts/registration.html"


@capture.enable
class StudentDetailVerificationView(generic.View):
    """View for verifying student details existence"""

    http_method_names = ["post"]
    form_class = StudentDetailVerificationForm

    @capture.capture(content="Oops! An error occurred while verifying your details.")
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

        student = get_student(**form.cleaned_data)
        if not student:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Sorry, we could not verify your details. Please try again.",
                },
                status=400,
            )

        if student.account:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "You have already registered an account. Proceed to sign in.",
                    "redirect_url": reverse("accounts:signin"),
                },
                status=400,
            )

        with transaction.atomic():
            totp = generate_totp_for_identifier(student.id)
            send_otp(totp.token(), recipient=student.email)

        return JsonResponse(
            data={
                "status": "success",
                "detail": f"Hi {student}! Your details have been verified. Check your email for an OTP to proceed",
            },
            status=200,
        )


@capture.enable
class RegistrationOTPVerificationView(generic.View):
    """View for verifying registration OTP"""

    http_method_names = ["post"]
    form_class = RegistrationOTPVerificationForm

    @capture.capture(content="Oops! An error occurred while verifying OTP.")
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

        form_data = form.cleaned_data.copy()
        otp = form_data.pop("otp")
        student = get_student(**form_data)
        if not student:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Invalid payload!",
                },
                status=400,
            )

        with transaction.atomic():
            is_valid = verify_identifier_totp_token(token=otp, identifier=student.id)
            # is_valid = dummy_verify_totp_token(token=otp, identifier=student.id)
            if not is_valid:
                return JsonResponse(
                    data={
                        "status": "error",
                        "detail": "Invalid OTP.",
                    },
                    status=400,
                )

            password_set_token = exchange_data_for_token(
                data={
                    "student_id": str(student.id),
                },
                expires_after=60 * 15,
            )
        return JsonResponse(
            data={
                "status": "success",
                "detail": "Valid OTP!",
                "data": {
                    "password_set_token": password_set_token,
                },
            },
            status=200,
        )


@capture.enable
class RegistrationCompletionView(generic.CreateView):
    """View for user regsitration completion"""

    http_method_names = ["post"]
    form_class = RegistrationCompletionForm

    @capture.capture(content="Oops! An error occurred while completing registration.")
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

        form_data = form.cleaned_data.copy()
        password = form_data.get("password")
        password_set_token = form_data.pop("password_set_token")
        timezone = form_data.pop("timezone", None)

        with transaction.atomic():
            with capture.capture(
                (Student.DoesNotExist, InvalidToken),
                content="Session expired. Please refresh and try again.",
                code=400,
            ):
                data = exchange_token_for_data(password_set_token)
                student_id = data.get("student_id")
                student = Student.objects.get(id=student_id)

            account = create_account_for_student(
                student.email, student.name, password=password
            )

            if timezone:
                account.timezone = timezone
                account.save()
            student.account = account
            student.save()
            # Just log in the user after registration
            # Make sure to use the custom authentication backend for student users
            login(
                request,
                account,
                backend="apps.accounts.auth_backends.StudentUserAuthenticationBackend",
            )

        return JsonResponse(
            data={
                "status": "success",
                "detail": "Registration successful!",
                "redirect_url": reverse("accounts:signin"),
            },
            status=200,
        )


########################
# PASSWORD RESET VIEWS #
########################


@redirect_authenticated("elections:election_list")
class PasswordResetView(generic.TemplateView):
    template_name = "accounts/password_reset.html"


@capture.enable
class PasswordResetInitiationView(generic.View):
    """View for password reset initiation"""

    http_method_names = ["post"]
    form_class = PasswordResetInitiationForm

    @capture.capture(content="Oops! An error occurred while verifying your details.")
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

        account = UserAccount.objects.filter(
            email__iexact=form.cleaned_data["email"]
        ).first()
        if not account:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Sorry, we could not identify you. Please try again.",
                },
                status=400,
            )

        with transaction.atomic():
            totp = generate_totp_for_identifier(account.id)
            send_otp(totp.token(), recipient=account.email)

        return JsonResponse(
            data={
                "status": "success",
                "detail": "Check your email for an OTP to proceed",
            },
            status=200,
        )


@capture.enable
class PasswordResetOTPVerificationView(generic.View):
    """View for verifying password reset OTP"""

    http_method_names = ["post"]
    form_class = PasswordResetOTPVerificationForm

    @capture.capture(content="Oops! An error occurred while verifying OTP.")
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

        form_data = form.cleaned_data.copy()
        otp = form_data.pop("otp")
        account = UserAccount.objects.filter(email__iexact=form_data["email"]).first()
        if not account:
            return JsonResponse(
                data={
                    "status": "error",
                    "detail": "Invalid payload!",
                },
                status=400,
            )

        with transaction.atomic():
            is_valid = verify_identifier_totp_token(token=otp, identifier=account.id)
            # is_valid = dummy_verify_totp_token(token=otp, identifier=student.id)
            if not is_valid:
                return JsonResponse(
                    data={
                        "status": "error",
                        "detail": "Invalid OTP.",
                    },
                    status=400,
                )

            password_reset_token = exchange_data_for_token(
                data={
                    "account_id": str(account.id),
                },
                expires_after=60 * 15,
            )
        return JsonResponse(
            data={
                "status": "success",
                "detail": "Valid OTP!",
                "data": {
                    "password_reset_token": password_reset_token,
                },
            },
            status=200,
        )


@capture.enable
class PasswordResetCompletionView(generic.CreateView):
    """View for password reset completion"""

    http_method_names = ["post"]
    form_class = PasswordResetCompletionForm

    @capture.capture(content="Oops! An error occurred while completing password reset.")
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

        form_data = form.cleaned_data.copy()
        password = form_data.get("password")
        password_reset_token = form_data.pop("password_reset_token")

        with transaction.atomic():
            with capture.capture(
                (UserAccount.DoesNotExist, InvalidToken),
                content="The reset token is invalid or expired.",
                code=400,
            ):
                data = exchange_token_for_data(password_reset_token)
                account_id = data.get("account_id")
                account = UserAccount.objects.get(id=account_id)

            account.set_password(password)
            account.save()
            login(
                request,
                account,
                backend="apps.accounts.auth_backends.StudentUserAuthenticationBackend",
            )

        return JsonResponse(
            data={
                "status": "success",
                "detail": "Password reset successful!",
                "redirect_url": reverse("accounts:signin"),
            },
            status=200,
        )


user_signin_view = SignInView.as_view()
user_signout_view = SignOutView.as_view()

registration_view = RegistrationView.as_view()
student_detail_verification_view = StudentDetailVerificationView.as_view()
registration_otp_verification_view = RegistrationOTPVerificationView.as_view()
registration_completion_view = RegistrationCompletionView.as_view()

password_reset_view = PasswordResetView.as_view()
password_reset_initiation_view = PasswordResetInitiationView.as_view()
password_reset_otp_verification_view = PasswordResetOTPVerificationView.as_view()
password_reset_completion_view = PasswordResetCompletionView.as_view()
