import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _split_env_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def _get_env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"A variável de ambiente {name} é obrigatória.")
    return value


def _build_csrf_trusted_origins(allowed_hosts, configured_origins, app_port=None, debug=False):
    trusted = []
    seen = set()

    def add(origin):
        if origin and origin not in seen:
            trusted.append(origin)
            seen.add(origin)

    for origin in configured_origins:
        add(origin)

    for host in allowed_hosts:
        normalized_host = host.lstrip(".")
        if not normalized_host or normalized_host == "*":
            continue
        if normalized_host.startswith("[") and normalized_host.endswith("]"):
            continue
        add(f"http://{normalized_host}")
        add(f"https://{normalized_host}")
        if app_port:
            add(f"http://{normalized_host}:{app_port}")
            add(f"https://{normalized_host}:{app_port}")

    if debug:
        add("https://*.app.github.dev")
        add("https://*.githubpreview.dev")

    return trusted

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in {"1", "true", "yes", "on"}
APP_PORT = os.environ.get("DJANGO_APP_PORT", "2332").strip()
ALLOWED_HOSTS = _split_env_list(os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,0.0.0.0"))
CSRF_TRUSTED_ORIGINS = _build_csrf_trusted_origins(
    ALLOWED_HOSTS,
    _split_env_list(
        os.environ.get(
            "DJANGO_CSRF_TRUSTED_ORIGINS",
            "http://127.0.0.1,http://localhost,http://0.0.0.0",
        )
    ),
    app_port=APP_PORT,
    debug=DEBUG,
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "avaliacao.apps.AvaliacaoConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "sam_ti.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "sam_ti.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": _get_env("DB_NAME", "sam_ti", required=True),
        "USER": _get_env("DB_USER", "sam_ti_user", required=True),
        "PASSWORD": _get_env("DB_PASSWORD", "sam_ti_pass", required=True),
        "HOST": _get_env("DB_HOST", "127.0.0.1", required=True),
        "PORT": _get_env("DB_PORT", "3306", required=True),
    }
}

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

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Bahia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "nao-responda@samti.local")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
