from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path("sign-in/", views.user_signin_view, name="signin"),
    path("sign-out/", views.user_signout_view, name="signout"),
    path("registration/", views.registration_view, name="registration"),
    path(
        "registration/detail-verification/",
        views.student_detail_verification_view,
        name="student_detail_verification",
    ),
    path(
        "registration/otp-verification/",
        views.registration_otp_verification_view,
        name="registration_otp_verification",
    ),
    path(
        "registration/completion/",
        views.registration_completion_view,
        name="registration_completion",
    ),
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path(
        "password-reset/initiate/",
        views.password_reset_initiation_view,
        name="password_reset_initiation",
    ),
    path(
        "password-reset/verification/",
        views.password_reset_otp_verification_view,
        name="password_reset_otp_verification",
    ),
    path(
        "password-reset/completion/",
        views.password_reset_completion_view,
        name="password_reset_completion",
    ),
]
