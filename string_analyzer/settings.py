from pathlib import Path
import os
from decouple import config
from dotenv import load_dotenv

# ----------------------------------------
# BASE DIRECTORY
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------
# ENVIRONMENT LOADING
# ----------------------------------------
# Priority: .env.environment (local) → .env (production) → Railway variables
env_file = BASE_DIR / ".env.environment" if os.path.exists(BASE_DIR / ".env.environment") else BASE_DIR / ".env"

if os.path.exists(env_file):
    load_dotenv(env_file)
    print(f"✅ Loaded environment file: {env_file.name}")
else:
    print("⚠️ No .env file found — using Railway environment variables")

# ----------------------------------------
# CORE SETTINGS
# ----------------------------------------
ENVIRONMENT = os.getenv("ENVIRONMENT", "local").lower()
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret")
DEBUG = True if ENVIRONMENT == "local" else False

if ENVIRONMENT == "local":
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ".railway.app,localhost,127.0.0.1").split(",")

# --------------------------------------------------
# DATABASES
# --------------------------------------------------
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": BASE_DIR / config("DB_NAME", default="db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    # Default Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "rest_framework",
    "drf_yasg",

    # Local apps
    "analyzer",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "string_analyzer.urls"
WSGI_APPLICATION = "string_analyzer.wsgi.application"

# --------------------------------------------------
# CORS
# --------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --------------------------------------------------
# REST FRAMEWORK
# --------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer" if DEBUG else "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "5/minute", "user": "20/minute"},
}

# --------------------------------------------------
# SWAGGER (drf_yasg)
# --------------------------------------------------
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "DEFAULT_INFO": "string_analyzer.urls.api_info",
}
REDOC_SETTINGS = {"LAZY_RENDERING": True}

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# --------------------------------------------------
# PASSWORD VALIDATORS
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
            "level": "WARNING",
        },
    },
    "loggers": {
        "django": {"handlers": ["console", "file"], "level": "WARNING"},
        "api": {"handlers": ["console", "file"], "level": "INFO"},
    },
}

# --------------------------------------------------
# DEFAULT FIELD
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# ENVIRONMENT PRINT
# --------------------------------------------------
print(f"✅ Running in {ENVIRONMENT.upper()} mode | DEBUG={DEBUG}")
