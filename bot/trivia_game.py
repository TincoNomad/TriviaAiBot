from typing import Tuple, List, Dict, Any, Optional
from .api_client import TriviaAPIClient
from .utils.logging_bot import game_logger
from .utils.utils import get_theme_list, get_difficulty_list
from api.django import TRIVIA_URL

class TriviaGame:
    def __init__(self) -> None:
        self.api_client = TriviaAPIClient()
        self.game_data: List[Dict[str, Any]] = []
        self.current_trivia: List[Dict[str, Any]] = []
        self.difficulty_choices: Dict[int, str] = {}
        self.theme_choices: Dict[int, str] = {}
        
    async def initialize(self) -> None:
        async with self.api_client as client:
            try:
                self.game_data = await client.get(TRIVIA_URL)
                _, self.difficulty_choices = await get_difficulty_list()
                _, self.theme_choices = await get_theme_list()
                game_logger.info("Trivia game initialized successfully")
            except Exception as e:
                game_logger.error(f"Failed to initialize trivia game: {e}")
                raise
    
    async def get_available_options(self) -> Tuple[str, str]:
        """Returns the formatted lists of themes and difficulties available"""
        theme_list, _ = await get_theme_list()
        difficulty_list, _ = await get_difficulty_list()
        return theme_list, difficulty_list
    
    async def get_trivia(self, theme_id: str, difficulty_level: int) -> Tuple[str, int]:
        try:
            filtered_trivias = await self.api_client.get_filtered_trivias(theme_id, difficulty_level)
            
            if not filtered_trivias:
                return "No trivias available for this combination", 0
                
            trivia_list = "\n".join(
                f"{idx + 1}- {trivia['title']}" 
                for idx, trivia in enumerate(filtered_trivias)
            )
            
            self.current_trivia = filtered_trivias
            return trivia_list, len(filtered_trivias)
            
        except Exception as e:
            game_logger.error(f"Error getting trivias: {e}")
            raise
    
    def get_question(self, selected_trivia: str, question_counter: int) -> Tuple[str, int, int]:
        try:
            trivia = next(
                (trivia for trivia in self.current_trivia if trivia["title"] == selected_trivia),
                None
            )
            
            if not trivia or "questions" not in trivia:
                game_logger.error(f"No questions found for trivia: {selected_trivia}")
                return "Error getting the question", 0, 0
                
            question = trivia["questions"][question_counter]
            correct_answer = next(
                (i+1 for i, a in enumerate(question["answers"]) if a["is_correct"]),
                0
            )
            return question["question_title"], correct_answer, question["points"]
            
        except Exception as e:
            game_logger.error(f"Error getting question: {e}")
            return "Error processing question data", 0, 0
            
    def get_link(self, selected_trivia: str) -> Optional[str]:
        try:
            trivia = next(
                (trivia for trivia in self.current_trivia if trivia["title"] == selected_trivia),
                None
            )
            if trivia and trivia.get("url"):
                return trivia["url"]
            return None
        except Exception as e:
            game_logger.error(f"Error getting trivia link: {e}")
            return None
