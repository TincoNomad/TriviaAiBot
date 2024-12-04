from typing import Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class PlayerGame:
    channel_id: int
    current_score: int
    current_question: int
    selected_trivia: Optional[str] = None
    total_questions: int = 5
    leaderboard_id: Optional[str] = None

class GameState:
    def __init__(self):
        self.active_games: Dict[int, PlayerGame] = {}  # user_id -> PlayerGame
        self.user_selections: Dict[int, Dict[str, Any]] = {}  # user_id -> {theme, difficulty, etc}
