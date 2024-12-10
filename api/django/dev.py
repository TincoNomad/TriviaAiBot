from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Only define BASE_URL, other URLs are constructed in __init__.py
BASE_URL = 'http://127.0.0.1:8000'

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'