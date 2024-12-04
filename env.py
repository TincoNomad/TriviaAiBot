import environ
import os

# Initialize environ
env = environ.Env(
    ENVIRONMENT=(str, 'development'),
    DEBUG=(bool, True),
    SECRET_KEY=(str, None),
    SIGNING_KEY=(str, None),
)

# Read the .env file
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '.env'))

# Determine environment
IS_DEVELOPMENT = env('ENVIRONMENT') == 'development'
