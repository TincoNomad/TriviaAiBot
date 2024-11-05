import os
from .base import *  # noqa: F403

environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
if environment == 'production':
    from .prod import LEADERBOARD_URL, SCORE_URL, QUESTION_URL
else:
    from .dev import LEADERBOARD_URL, SCORE_URL, QUESTION_URL
