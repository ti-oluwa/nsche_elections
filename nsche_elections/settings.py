import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

APPLICATION_NAME = os.getenv("APPLICATION_NAME")

APPLICATION_ALIAS = os.getenv("APPLICATION_ALIAS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
]

MIDDLEWARE = [
    "helpers.response.middleware.MaintenanceMiddleware",  # Handles application maintenance mode
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "nsche_elections.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "nsche_elections.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

CONN_MAX_AGE = 60

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = []

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static/")


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGIN_URL = "accounts:signin"

if DEBUG is False:
    # PRODUCTION SETTINGS ONLY
    ALLOWED_HOSTS = ["*"]

else:
    # DEVELOPMENT SETTINGS ONLY
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]


CSRF_TRUSTED_ORIGINS = ["https://*"]

####################
# HELPERS SETTINGS #
####################

HELPERS_SETTINGS = {
    "MAINTENANCE_MODE": {
        "status": os.getenv("MAINTENANCE_MODE", "off").lower() in ["on", "true"],
        "message": os.getenv("MAINTENANCE_MODE_MESSAGE", "default:minimal_dark"),
    },
}
