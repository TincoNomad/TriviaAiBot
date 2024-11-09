import logging
from ..api_client import TriviaAPIClient
from api.django import THEME_URL, DIFFICULTY_URL
from typing import Tuple, Dict, Any

# Constants
TIMEOUT_DURATION = 30
MAX_QUESTIONS = 5
POINTS_PER_CORRECT_ANSWER = 10

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_theme_list() -> Tuple[str, Dict[int, Dict[str, Any]]]:
    try:
        async with TriviaAPIClient() as client:
            themes = await client.get(THEME_URL)
            print(f"DEBUG Utils - Received themes from API: {themes}")
            
            theme_dict = {i+1: {'id': theme['id'], 'name': theme['name']} 
                         for i, theme in enumerate(themes)}
            print(f"DEBUG Utils - Created theme_dict: {theme_dict}")
            
            theme_list = "\n".join(
                f"{num}- {theme['name']}" 
                for num, theme in theme_dict.items()
            )
            
            return theme_list, theme_dict
    except Exception as e:
        logger.error(f"Error getting theme list: {e}")
        raise

async def get_difficulty_list() -> Tuple[str, Dict[int, str]]:
    try:
        async with TriviaAPIClient() as client:
            difficulties = await client.get(DIFFICULTY_URL)
            
            difficulty_list = "\n".join(
                f"{level}- {name}" 
                for level, name in difficulties.items()
            )
            
            return difficulty_list, difficulties
    except Exception as e:
        logger.error(f"Error getting difficulty list: {e}")
        raise