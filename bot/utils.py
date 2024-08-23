import logging
from enum import Enum


# Constants
TIMEOUT_DURATION = 30
MAX_QUESTIONS = 5
POINTS_PER_CORRECT_ANSWER = 10

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class School(Enum):
    DEVELOPING = 1
    DATA_MLEARNING = 2
    MARKETING = 3
    DESIGN = 4
    SOFT_SKILLS = 5
    BUSINESS = 6
    FINANZAS = 7
    DIGITAL_CONTENT = 8
    STARTUP = 9
    ENGLISH = 10

class Difficulty(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3