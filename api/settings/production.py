from .base import *
from config import IS_DEVELOPMENT, LEADERBOARD_URL, SCORE_URL, QUESTION_URL

DEBUG = False
ALLOWED_HOSTS = ['your-production-domain.com']

BASE_URL = 'https://your-production-url.com/api'

def get_full_url(relative_url):
    return f"{BASE_URL}{relative_url}"

FULL_LEADERBOARD_URL = get_full_url(LEADERBOARD_URL)
FULL_SCORE_URL = get_full_url(SCORE_URL)
FULL_QUESTION_URL = get_full_url(QUESTION_URL)

# Add any production-specific settings here
