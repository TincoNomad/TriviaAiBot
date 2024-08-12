import os
from dotenv import load_dotenv

load_dotenv()

# Determine if we are in development or production
IS_DEVELOPMENT = os.environ.get('ENVIRONMENT', 'development') == 'development'

# Define base URLs
BASE_URL = 'http://127.0.0.1:8000/api' if IS_DEVELOPMENT else 'https://your-production-url.com/api'

# Define specific routes
LEADERBOARD_URL = f'{BASE_URL}/score/leaderboard'
SCORE_URL = f'{BASE_URL}/score'
QUESTION_URL = f'{BASE_URL}/question'

# Keys
DJANGO_KEY = os.environ.get('SECRET_KEY')
DISCORD_KEY = os.environ.get('DISCORD_KEY')