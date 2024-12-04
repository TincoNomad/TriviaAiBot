import os
from .base import *  # noqa: F403

environment = os.environ.get('DJANGO_ENVIRONMENT', 'development')
if environment == 'production':
    from .prod import (
        BASE_URL, TRIVIA_URL, THEME_URL, 
        DIFFICULTY_URL, FILTER_URL,
        LEADERBOARD_URL, SCORE_URL, QUESTION_URL
    )
else:
    from .dev import (
        BASE_URL, TRIVIA_URL, THEME_URL, 
        DIFFICULTY_URL, FILTER_URL,
        LEADERBOARD_URL, SCORE_URL, QUESTION_URL
    )

__all__ = [
    'BASE_URL', 'TRIVIA_URL', 'THEME_URL', 
    'DIFFICULTY_URL', 'FILTER_URL',
    'LEADERBOARD_URL', 'SCORE_URL', 'QUESTION_URL'
]
