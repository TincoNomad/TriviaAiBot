import os
from .base import *  # noqa: F403
# from .base import DEBUG, ALLOWED_HOSTS, DATABASES, INSTALLED_APPS, MIDDLEWARE


# Importar explícitamente las configuraciones que podrían ser sobrescritas
environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
if environment == 'production':
    from .production import FULL_LEADERBOARD_URL, FULL_SCORE_URL, FULL_QUESTION_URL
else:
    from .development import FULL_LEADERBOARD_URL, FULL_SCORE_URL, FULL_QUESTION_URL
