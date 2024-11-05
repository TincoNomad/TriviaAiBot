from .base import *
from env import IS_DEVELOPMENT

DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

# URLs base y específicas
BASE_URL = 'https://your-production-url.com/api'
LEADERBOARD_URL = f"{BASE_URL}/score/leaderboard"
SCORE_URL = f"{BASE_URL}/score"
QUESTION_URL = f"{BASE_URL}/question"

# Add any production-specific settings here
