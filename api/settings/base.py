import os
import sys
from pathlib import Path
from config import DJANGO_KEY
from typing import List

# Set up the project root and add it to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Define the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Import the secret key from the config file
SECRET_KEY = DJANGO_KEY

# Debug mode is set to True by default (should be False in production)
DEBUG = True

# List of allowed hosts (empty by default, should be set in production)
ALLOWED_HOSTS: List[str] = []

# Application definition
# List of installed Django apps and third-party packages
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom apps
    'api.apps.trivia.apps.TriviaConfig',
    'api.apps.score.apps.ScoreConfig',
    'api.apps.users.apps.UsersConfig',
    # Third-party apps
    'rest_framework',
    'whitenoise.runserver_nostatic',
]

# Middleware configuration
# List of middleware classes for request/response processing
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # WhiteNoise for static file serving
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# Root URL configuration
ROOT_URLCONF = 'api.urls'

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# WSGI application path
WSGI_APPLICATION = 'api.wsgi.application'

# Database configuration (using SQLite by default)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation settings
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

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'