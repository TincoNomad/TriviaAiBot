from .base import *
from env import IS_DEVELOPMENT

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# URLs base y específicas
BASE_URL = 'http://127.0.0.1:8000/api'
LEADERBOARD_URL = f"{BASE_URL}/score/leaderboard"
SCORE_URL = f"{BASE_URL}/score"
QUESTION_URL = f"{BASE_URL}/question"

# Development-specific settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Add any other development-specific settings here