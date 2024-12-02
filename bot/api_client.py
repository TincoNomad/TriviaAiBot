import aiohttp
from typing import Dict, Any, Optional, List
from typing_extensions import Self
from .utils.logging_bot import bot_logger
from api.django import (
    FILTER_URL, LEADERBOARD_URL, SCORE_URL, QUESTION_URL, BASE_URL
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
            
    async def get(self, url: str) -> Any:
        """Método genérico para hacer peticiones GET"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            bot_logger.error(f"Error en petición GET a {url}: {e}")
            raise
            
    async def post(self, url: str, data: Dict[str, Any], use_csrf: bool = True) -> Any:
        """Método genérico para hacer peticiones POST"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        try:
            headers = {'Content-Type': 'application/json'}            
            if use_csrf:
                csrf_token = await self.get_csrf_token()
                if csrf_token is None:
                    raise ValueError("No se pudo obtener el token CSRF")
                headers['X-CSRFToken'] = csrf_token
                
            async with self.session.post(url, json=data, headers=headers) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            bot_logger.error(f"Error en petición POST a {url}: {e}")
            raise
            
    async def get_csrf_token(self) -> Optional[str]:
        """Obtiene el token CSRF del servidor"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.get(SCORE_URL) as response:
                csrf_cookie = response.cookies.get('csrftoken')
                if csrf_cookie is None:
                    bot_logger.error("No se encontró el token CSRF en las cookies")
                    return None
                    
                self.csrf_token = csrf_cookie.value
                return self.csrf_token
        except Exception as e:
            bot_logger.error(f"Error obteniendo CSRF token: {e}")
            return None
            
    async def fetch_trivia_questions(self) -> List[Dict[str, Any]]:
        """Gets trivia questions from the API"""
        return await self.get(QUESTION_URL)
            
    async def get_filtered_trivias(self, theme: str, difficulty: int) -> List[Dict[str, Any]]:
        """Gets filtered trivia questions by theme and difficulty"""
        try:
            url = f"{FILTER_URL}?theme={theme}&difficulty={difficulty}"
            bot_logger.info(f"Requesting filtered trivias with URL: {url}")
            return await self.get(url)
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
        """Gets the score table for a specific discord channel"""
        data = {"discord_channel": discord_channel}
        return await self.post(LEADERBOARD_URL, data)
            
    async def update_score(self, name: str, points: int, discord_channel: str):
        """Actualiza el score usando el token CSRF
        
        Args:
            name (str): Nombre del usuario de Discord
            points (int): Puntos ganados en la pregunta
            discord_channel (str): Identificador del canal de Discord
            
        Returns:
            Dict: Datos actualizados del score
            
        Raises:
            ValueError: Si faltan datos requeridos o son inválidos
            ClientResponseError: Si hay errores de comunicación con el API
        """
        # Validaciones básicas
        if not name or not discord_channel:
            raise ValueError("El nombre y canal de Discord son requeridos")
        
        if not isinstance(points, (int, float)):
            raise ValueError("Los puntos deben ser un número")
        
        try:
            data = {
                "name": name,
                "points": points,
                "discord_channel": discord_channel
            }
            
            response = await self.post(f"{SCORE_URL}update_score/", data)
            
            # Verificar la respuesta exitosa
            if "message" in response and response["message"] == "Score updated successfully":
                bot_logger.info(
                    f"Score actualizado exitosamente - Usuario: {name}, "
                    f"Puntos: {points}, Canal: {discord_channel}"
                )
                return response["data"]
            
            # Si la respuesta no tiene el formato esperado
            bot_logger.error(f"Respuesta inesperada del servidor: {response}")
            raise ValueError("Error inesperado al actualizar el score")
            
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                bot_logger.error(f"Usuario o canal no encontrado: {name}, {discord_channel}")
                raise ValueError("Usuario o canal no encontrado")
            elif e.status in [401, 403]:
                bot_logger.error("Error de autorización al actualizar score")
                raise ValueError("Error de autorización")
            elif e.status == 400:
                bot_logger.error(f"Datos inválidos enviados al servidor: {data}")
                raise ValueError("Datos inválidos para actualizar score")
            else:
                bot_logger.error(f"Error del servidor al actualizar score: {e}")
                raise
        except aiohttp.ClientError as e:
            bot_logger.error(f"Error de conexión al actualizar score: {e}")
            raise ValueError("Error de conexión con el servidor")
        except Exception as e:
            bot_logger.error(f"Error inesperado actualizando score: {e}")
            raise ValueError(f"Error inesperado: {str(e)}")
            
    async def create_leaderboard(self, discord_channel: str, username: str) -> Dict[str, Any]:
        """Crea un nuevo leaderboard para el canal"""
        data = {
            "discord_channel": discord_channel,
            "username": username
        }
        return await self.post(LEADERBOARD_URL, data)