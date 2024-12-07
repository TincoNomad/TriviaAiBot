from discord import Message, Client
from .trivia_player import TriviaPlayer
from .trivia_creator import TriviaCreator

class TriviaCommands:
    def __init__(self, client: Client):
        self.game_handler = TriviaPlayer(client)
        self.trivia_creator = TriviaCreator(client)
        
    async def handle_trivia(self, message: Message) -> None:
        """Route trivia game command to game handler"""
        await self.game_handler.handle_trivia(message)
        
    async def handle_create_trivia(self, message: Message) -> None:
        """Route trivia creation command to creator"""
        await self.trivia_creator.handle_create_trivia(message)
        
    async def handle_score(self, message: Message) -> None:
        """Route score command to game handler"""
        await self.game_handler.handle_score(message)
        
    async def handle_themes(self, message: Message) -> None:
        """Route themes command to game handler"""
        await self.game_handler.handle_themes(message)
        
    async def handle_game_response(self, message: Message) -> None:
        """Route game responses to game handler"""
        await self.game_handler.handle_game_response(message)
        
    async def handle_stop_game(self, message: Message) -> None:
        """Route stop game command to game handler"""
        await self.game_handler.handle_stop_game(message)