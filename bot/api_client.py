import aiohttp
from typing import Dict, Any, Optional, List
from typing_extensions import Self
from .utils.logging_bot import bot_logger
from api.django import (
    FILTER_URL, LEADERBOARD_URL, SCORE_URL, QUESTION_URL
)

class TriviaAPIClient:
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        if self.session:
            await self.session.close()
            
    async def get(self, url: str) -> Any:
        """Generic method for making GET requests"""
        try:
            bot_logger.info(f"GET request to: {url}")
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                bot_logger.debug(f"Received data from {url}")
                return data
        except Exception as e:
            bot_logger.error(f"Error in GET request to {url}: {e}")
            raise
            
    async def fetch_trivia_questions(self) -> List[Dict[str, Any]]:
        """Gets trivia questions from the API"""
        return await self.get(QUESTION_URL)
            
    async def get_filtered_trivias(self, theme: str, difficulty: int) -> List[Dict[str, Any]]:
        """Gets filtered trivia questions by theme and difficulty"""
        url = f"{FILTER_URL}/?theme={theme}&difficulty={difficulty}"
        return await self.get(url)
            
    async def get_leaderboard(self) -> List[Dict[str, Any]]:
        """Gets the score table"""
        return await self.get(LEADERBOARD_URL)
            
    async def update_score(self, name: str, points: int) -> bool:
        """Updates the score of a player"""
        try:
            bot_logger.info(f"Updating score for {name}: {points} points")
            if not self.session:
                self.session = aiohttp.ClientSession()
            async with self.session.post(SCORE_URL, json={
                "name": name,
                "points": points
            }) as response:
                return response.status == 201
        except Exception as e:
            bot_logger.error(f"Error updating score: {e}")
            return False