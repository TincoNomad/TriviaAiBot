from .base import *
from config import IS_DEVELOPMENT, LEADERBOARD_URL, SCORE_URL, QUESTION_URL

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

BASE_URL = 'http://127.0.0.1:8000/api'

def get_full_url(relative_url):
    return f"{BASE_URL}{relative_url}"

FULL_LEADERBOARD_URL = get_full_url(LEADERBOARD_URL)
FULL_SCORE_URL = get_full_url(SCORE_URL)
FULL_QUESTION_URL = get_full_url(QUESTION_URL)

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add any other development-specific settings here
