"""
Django settings for the andromeda project.

Generated by 'django-admin startproject' using Django 4.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import os
import environ
import django_heroku
from datetime import timedelta



env = environ.Env(
    # set casting, default value
    # DEBUG=(bool, False)
)



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-8kq0ta)$9di^j855*z*f=z-oxm)v@+=s#m1qiijma(qo6sik2)'
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = env('DEBUG') == 'True'

# Crystal API KEY
CRYSTAL_API_KEY = env('CRYSTALBC_KEY')

ALLOWED_HOSTS = [
    'http://chainvet-frontend.herokuapp.com',
    'http://chainvet-backend.herokuapp.com',
    'http://185.165.169.144',
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
    "http://localhost:8000",
    ]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://185.165.169.144",
    "https://185.165.169.144",
]

CORS_ALLOWED_ORIGINS = [
    'https://chainvet-frontend.herokuapp.com',
    'https://chainvet-backend.herokuapp.com',
    'http://185.165.169.144',
    'https://185.165.169.144',
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# Reference: https://stackoverflow.com/questions/73594763/django-forbidden-403-origin-checking-failed-csrf-failed

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        #'rest_framework.permissions.AllowAny',
        'rest_framework.permissions.IsAuthenticated',
    )
}

# CHAINVET APP API KEY HEADER
API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY"

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60*24), # XYZ THIS IS SUB-OPTIMAL FOR SAFETY,
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=60*24*7),
    "BLACKLIST_AFTER_ROTATION": False,
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_api_key',
    'corsheaders',
    'djoser',
    'guardian',

    'apps.users',
    'apps.logManager',
    'apps.featureAccessControl',
    'apps.surveys',

    'apps.chainvet',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'andromeda.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['emailAuthTemplates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'andromeda.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
if env('ENVIRONMENT') == 'DEV':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    db_password = env('POSTGRES_PASSWORD')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'andromeda_db',
            'USER': 'andromeda_db',
            'PASSWORD': db_password,
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication backends (django-guardian documentation)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)
GUARDIAN_AUTO_PREFETCH = False # False is default


### LOGGING - START ###
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime} - {levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'stdout': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'api_calls_trocador': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'api_calls_trocador.log',
            'formatter': 'verbose',
        },
        'api_calls_cbc': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'api_calls_cbc.log',
            'formatter': 'verbose',
        },
        'coinpaprika': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'coinpaprika.log',
            'formatter': 'verbose',
        },
        'error_log_handler': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'errors.log',
            'formatter': 'verbose',
        },
        'request_timing': {
            'level': 'DEBUG',
            'class': 'logging.handlers.FileHandler',  # Use TimedRotatingFileHandler
            'filename': 'request_timing.log',
            'formatter': 'verbose',
            # 'when': 'midnight',  # Rotate at midnight
            # 'interval': 1,  # Every day
            # 'backupCount': 7,  # Keep 7 days worth
        },
    },
    'loggers': {
        'api_calls_trocador': {
            'handlers': ['api_calls_trocador'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'api_calls_cbc': {
            'handlers': ['api_calls_cbc'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'error_logger': {
            'handlers': ['error_log_handler'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'request_timing': {
            'handlers': ['request_timing'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'coinpaprika': {
            'handlers': ['coinpaprika'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
    'root': {
        'handlers': ['stdout'],
        'level': 'DEBUG',
    },
}
### LOGGING - END ###

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

#CACHE SETTINGS
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'core_cache_table',
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# STATIC_URL = 'static/'
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static')
# ]
# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# Redirecting/Setting the default user model
AUTH_USER_MODEL = 'users.CustomUser'


# Djoser Related Settings
DOMAIN = env('DOMAIN')
SITE_NAME = 'Andromeda'
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_RETYPE': True,
    'SET_PASSWORD_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'reset-senha/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'reset-email/confirm/{uid}/{token}',
    # 'ACTIVATION_URL': 'ativacao-de-conta/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        # 'user_create': 'apps.users.serializers.UserCreateSerializer',
        'user': 'apps.users.serializers.CustomUserSerializer',
        'current_user': 'apps.users.serializers.CustomUserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
    # Reference stops here (the rest is autopilot)
    'LOGIN_AFTER_ACTIVATION': False,
    'USERNAME_REQUIRED': False,
    'EMAIL': {
        'activation': 'emailAuthTemplates.email.ActivationEmail',
        'confirmation': 'emailAuthTemplates.email.ConfirmationEmail',
        'password_reset': 'emailAuthTemplates.email.PasswordResetEmail',
        'password_changed_confirmation': 'emailAuthTemplates.email.PasswordChangedConfirmationEmail',
        'username_changed_confirmation': 'emailAuthTemplates.email.UsernameChangedConfirmationEmail',
        'username_reset': 'emailAuthTemplates.email.UsernameResetEmail',
    }
}

# Authentication Email Settings
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = int(env('EMAIL_PORT'))
EMAIL_USE_TLS = env('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# USE_TZ = False


## CELERY SETTINGS
CELERY_BROKER_URL = 'redis://localhost:6379'  
CELERY_RESULT_BACKEND = 'redis://localhost:6379'  
CELERY_ACCEPT_CONTENT = ['application/json']  
CELERY_TASK_SERIALIZER = 'json'  
CELERY_RESULT_SERIALIZER = 'json'  
CELERY_TIMEZONE = "UTC"

django_heroku.settings(locals())