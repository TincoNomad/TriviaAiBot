import aiohttp
from typing import Dict, Any, Optional, List
from typing_extensions import Self
from .utils.logging_bot import bot_logger
from api.django import (
    FILTER_URL, LEADERBOARD_URL, SCORE_URL, QUESTION_URL, BASE_URL, TRIVIA_URL
)

class TriviaAPIClient:
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        self.csrf_token: Optional[str] = None
        self.base_url = BASE_URL
        
    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        if self.session:
            await self.session.close()
            
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Generic method for making GET requests with query parameters
        
        Args:
            url (str): The URL to make the request to
            params (Optional[Dict[str, Any]]): Query parameters to include in the URL
            
        Returns:
            Any: The JSON response from the server
            
        Raises:
            Exception: If there is an error making the request
            
        Note:
            This method uses query parameters (added to URL) instead of a JSON body,
            following REST conventions for GET requests.
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            bot_logger.debug(f"Making GET request to {url} with params: {params}")
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            bot_logger.error(f"Error in GET request to {url}: {e}")
            raise
            
    async def post(self, url: str, data: Dict[str, Any], use_csrf: bool = True) -> Any:
        """Generic method for making POST requests"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            headers = {'Content-Type': 'application/json'}            
            if use_csrf:
                csrf_token = await self.get_csrf_token()
                if csrf_token is None:
                    raise ValueError("Could not obtain CSRF token")
                headers['X-CSRFToken'] = csrf_token
                
            bot_logger.info(f"Making POST request to {url}")
            bot_logger.debug(f"Request data: {data}")
            bot_logger.debug(f"Headers: {headers}")
            
            async with self.session.post(url, json=data, headers=headers) as response:
                response_text = await response.text()
                bot_logger.debug(f"Response status: {response.status}")
                bot_logger.debug(f"Response text: {response_text}")
                
                try:
                    response.raise_for_status()
                    return await response.json()
                except aiohttp.ClientResponseError as e:
                    bot_logger.error(f"HTTP Error in POST request to {url}: {e.status} - {e.message}")
                    bot_logger.error(f"Response body: {response_text}")
                    raise
            
        except Exception as e:
            bot_logger.error(f"Error in POST request to {url}: {str(e)}")
            raise
            
    async def get_csrf_token(self) -> Optional[str]:
        """Gets the CSRF token from the server"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(SCORE_URL) as response:
                csrf_cookie = response.cookies.get('csrftoken')
                if csrf_cookie is None:
                    bot_logger.error("CSRF token not found in cookies")
                    return None
                    
                self.csrf_token = csrf_cookie.value
                return self.csrf_token
        except Exception as e:
            bot_logger.error(f"Error obtaining CSRF token: {e}")
            return None
            
    async def fetch_trivia_questions(self) -> List[Dict[str, Any]]:
        """Gets trivia questions from the API"""
        return await self.get(QUESTION_URL)
            
    async def get_filtered_trivias(self, theme: str, difficulty: int) -> List[Dict[str, Any]]:
        """Gets filtered trivia questions by theme and difficulty"""
        try:
            params = {
                "theme": theme,
                "difficulty": difficulty
            }
            bot_logger.info(f"Requesting filtered trivias with params: {params}")
            return await self.get(FILTER_URL, params=params)
        except aiohttp.ClientResponseError as e:
            if e.status in [401, 403]:
                bot_logger.error("Unauthorized access to filtered trivias endpoint")
                raise ValueError("Unauthorized access")
            bot_logger.error(f"Error getting filtered trivias: {e}")
            raise
        except Exception as e:
            bot_logger.error(f"Error getting filtered trivias: {e}")
            raise
            
    async def get_leaderboard(self, discord_channel: str) -> Dict[str, Any]:
        """Gets the score table for a specific discord channel
        
        Args:
            discord_channel (str): The discord channel identifier
            
        Returns:
            Dict[str, Any]: A dictionary containing the leaderboard data with scores
            
        Raises:
            ValueError: If the channel is not found
            Exception: For other API errors
        """
        try:
            bot_logger.info(f"Requesting leaderboard for channel: {discord_channel}")
            params = {
                "channel": discord_channel
            }
            response = await self.get(LEADERBOARD_URL, params)
            bot_logger.debug(f"Leaderboard response: {response}")
            return response
        except Exception as e:
            bot_logger.error(f"Error getting leaderboard for channel {discord_channel}: {e}")
            raise
            
    async def update_score(self, name: str, points: int, discord_channel: str):
        """Updates the score using CSRF token
        
        Args:
            name (str): Discord username
            points (int): Points earned in the question
            discord_channel (str): Discord channel identifier
            
        Returns:
            Dict: Updated score data
            
        Raises:
            ValueError: If required data is missing or invalid
            ClientResponseError: If there are communication errors with the API
        """
        # Basic validations
        if not name or not discord_channel:
            raise ValueError("Discord name and channel are required")
        
        if not isinstance(points, (int, float)):
            raise ValueError("Points must be a number")
        
        try:
            data = {
                "name": name,
                "points": points,
                "discord_channel": discord_channel
            }
            
            response = await self.post(f"{SCORE_URL}", data)
            
            # Verify successful response
            if "message" in response and response["message"] == "Score updated successfully":
                bot_logger.info(
                    f"Score updated successfully - User: {name}, "
                    f"Points: {points}, Channel: {discord_channel}"
                )
                return response["data"]
            
            # If the response is not in the expected format
            bot_logger.error(f"Unexpected response from server: {response}")
            raise ValueError("Unexpected error updating score")
            
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                bot_logger.error(f"User or channel not found: {name}, {discord_channel}")
                raise ValueError("User or channel not found")
            elif e.status in [401, 403]:
                bot_logger.error("Authorization error updating score")
                raise ValueError("Authorization error")
            elif e.status == 400:
                bot_logger.error(f"Invalid data sent to server: {data}")
                raise ValueError("Invalid data for updating score")
            else:
                bot_logger.error(f"Server error updating score: {e}")
                raise
        except aiohttp.ClientError as e:
            bot_logger.error(f"Connection error updating score: {e}")
            raise ValueError("Connection error with the server")
        except Exception as e:
            bot_logger.error(f"Unexpected error updating score: {e}")
            raise ValueError(f"Unexpected error: {str(e)}")
            
    async def create_leaderboard(self, discord_channel: str, username: str) -> Dict[str, Any]:
        """Creates a new leaderboard for the channel"""
        data = {
            "discord_channel": discord_channel,
            "username": username
        }
        return await self.post(LEADERBOARD_URL, data)
            
    async def get_user_trivias(self, params: Dict[str, str]) -> List[Dict[str, Any]]:
        """Gets trivias created by a specific user
        
        Args:
            params (Dict[str, str]): Query parameters including username
            
        Returns:
            List[Dict[str, Any]]: List of trivias created by the user
            
        Raises:
            Exception: If there is an error getting the trivias
        """
        try:
            bot_logger.info(f"Getting trivias for user with params: {params}")
            response = await self.get(TRIVIA_URL, params)
            bot_logger.debug(f"Got trivias response: {response}")
            return response
        except Exception as e:
            bot_logger.error(f"Error getting user trivias: {e}")
            raise
            
    async def update_trivia(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a trivia question
        
        Args:
            data (Dict[str, Any]): Update data including trivia_id and the fields to update
            
        Returns:
            Dict[str, Any]: Updated trivia data
            
        Raises:
            Exception: If there is an error updating the trivia
        """
        try:
            trivia_id = data.pop('trivia_id')
            bot_logger.info(f"Updating trivia {trivia_id} with data: {data}")
            
            # Usar PATCH en lugar de POST para actualizar solo campos específicos
            response = await self.patch(f"{TRIVIA_URL}{trivia_id}/", data)
            bot_logger.debug(f"Update trivia response: {response}")
            return response
        except Exception as e:
            bot_logger.error(f"Error updating trivia: {e}")
            raise
            
    async def patch(self, url: str, data: Dict[str, Any]) -> Any:
        """Generic method for making PATCH requests"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            headers = {'Content-Type': 'application/json'}
            
            bot_logger.info(f"Making PATCH request to {url}")
            bot_logger.debug(f"Request data: {data}")
            
            async with self.session.patch(url, json=data, headers=headers) as response:
                response_text = await response.text()
                bot_logger.debug(f"Response status: {response.status}")
                bot_logger.debug(f"Response text: {response_text}")
                
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            bot_logger.error(f"Error in PATCH request to {url}: {str(e)}")
            raise
            
    async def patch_trivia(self, trivia_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Updates a trivia partially
        
        Args:
            trivia_id (str): ID of the trivia to update
            data (Dict[str, Any]): Fields to update
            
        Returns:
            Dict[str, Any]: Updated trivia data
        """
        try:
            bot_logger.info(f"Partially updating trivia {trivia_id} with data: {data}")
            response = await self.patch(f"{TRIVIA_URL}{trivia_id}/", data)
            bot_logger.debug(f"Update trivia response: {response}")
            return response
        except Exception as e:
            bot_logger.error(f"Error updating trivia: {e}")
            raise
            
    async def update_trivia_questions(self, trivia_id: str, questions_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Updates questions and answers for a trivia
        
        Args:
            trivia_id (str): ID of the trivia to update
            questions_data (List[Dict[str, Any]]): Questions and answers data to update
            
        Returns:
            Dict[str, Any]: Response from the API
            
        Raises:
            Exception: If there is an error updating the questions
        """
        try:
            data = {"questions": questions_data}
            bot_logger.info(f"Updating questions for trivia {trivia_id}")
            bot_logger.debug(f"Questions data: {questions_data}")
            
            response = await self.patch(f"{TRIVIA_URL}{trivia_id}/update_questions/", data)
            bot_logger.debug(f"Update questions response: {response}")
            return response
        except Exception as e:
            bot_logger.error(f"Error updating trivia questions: {e}")
            raise