import os
from .base import *  # noqa: F403
# from .base import DEBUG, ALLOWED_HOSTS, DATABASES, INSTALLED_APPS, MIDDLEWARE


# Import explicitly the configurations that could be overridden
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
if environment == 'production':
    from .prod import FULL_LEADERBOARD_URL, FULL_SCORE_URL, FULL_QUESTION_URL
else:
    from .dev import FULL_LEADERBOARD_URL, FULL_SCORE_URL, FULL_QUESTION_URL
