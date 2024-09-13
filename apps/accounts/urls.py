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
        views.otp_verification_view,
        name="otp_verification",
    ),
    path(
        "registration/completion/",
        views.registration_completion_view,
        name="registration_completion",
    ),
]
