from typing import Tuple, List, Dict, Any, Optional
from .api_client import TriviaAPIClient
from .utils.logging_bot import game_logger
from .utils.utils import get_theme_list, get_difficulty_list
from api.django import TRIVIA_URL, QUESTION_URL

POINTS_PER_CORRECT_ANSWER = 10

class TriviaGame:
    def __init__(self) -> None:
        self.api_client = TriviaAPIClient()
        self.game_data: List[Dict[str, Any]] = []
        self.current_trivia: List[Dict[str, Any]] = []
        self.difficulty_choices: Dict[int, str] = {}
        self.difficulty_choice: Optional[int] = None
        self.theme_choices: Dict[int, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        try:
            self.game_data = await self.api_client.get(TRIVIA_URL)
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
                return "No hay trivias disponibles para esta combinación", 0
                
            trivia_list = "\n".join(
                f"{idx + 1}- {trivia['title']}" 
                for idx, trivia in enumerate(filtered_trivias)
            )
            
            self.current_trivia = filtered_trivias
            return trivia_list, len(filtered_trivias)
                
        except Exception as e:
            game_logger.error(f"Error obteniendo trivias: {e}")
            raise
    
    async def get_trivia_questions(self, trivia_id: str) -> List[Dict[str, Any]]:
        """Gets questions for a specific trivia"""
        try:
            questions = await self.api_client.get(f"{QUESTION_URL}{trivia_id}/")
            return questions
        except Exception as e:
            game_logger.error(f"Error getting trivia questions: {e}")
            raise
    
    def get_question(self, questions: List[Dict], question_counter: int) -> Tuple[str, int, int, List[str]]:
        try:
            if not questions or question_counter >= len(questions):
                game_logger.error(f"No questions found or invalid counter: {question_counter}")
                return "Error getting the question", 0, 0, []
                
            question = questions[question_counter]
            correct_answer = next(
                (i+1 for i, a in enumerate(question["answers"]) if a["is_correct"]),
                0
            )
            
            answer_options = [
                f"{i+1}. {answer['answer_title']}" 
                for i, answer in enumerate(question["answers"])
            ]
            
            return question["question_title"], correct_answer, question["points"], answer_options
            
        except Exception as e:
            game_logger.error(f"Error getting question: {e}")
            return "Error processing question data", 0, 0, []
            
    def get_link(self, selected_trivia: str) -> Optional[str]:
        """Gets the course URL for the selected trivia"""
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
    
    async def set_difficulty(self, difficulty: int) -> None:
        """Sets the selected difficulty for the game"""
        if difficulty not in [1, 2, 3]:
            raise ValueError("Invalid difficulty")
        self.difficulty_choice = difficulty
        game_logger.debug(f"Difficulty set to: {difficulty}")
