from .base import *
from env import IS_DEVELOPMENT

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Base and specific URLs
BASE_URL = 'http://127.0.0.1:8000'
TRIVIA_URL = f"{BASE_URL}/api/trivias/"
THEME_URL = f"{BASE_URL}/api/themes/"
DIFFICULTY_URL = f"{TRIVIA_URL}difficulty/"
FILTER_URL = f"{TRIVIA_URL}filter/"
LEADERBOARD_URL = f"{BASE_URL}/api/leaderboards/"
SCORE_URL = f"{BASE_URL}/api/score/"
QUESTION_URL = f"{BASE_URL}/api/questions/"

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add any other development-specific settings here