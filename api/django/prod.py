from .base import *
from env import IS_DEVELOPMENT

DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

# Base and specific URLs
BASE_URL = 'https://your-production-url.com'
TRIVIA_URL = f"{BASE_URL}/api/trivias/"
THEME_URL = f"{BASE_URL}/api/themes/"
DIFFICULTY_URL = f"{TRIVIA_URL}difficulty/"
FILTER_URL = f"{TRIVIA_URL}filter/"
LEADERBOARD_URL = f"{BASE_URL}/api/score/leaderboard/"
SCORE_URL = f"{BASE_URL}/api/score/"
QUESTION_URL = f"{BASE_URL}/api/question/"

# Add any production-specific settings here
