from discord import Message, Client
from .trivia_player import TriviaPlayer
from .trivia_creator import TriviaCreator
from .trivia_updater import TriviaUpdater

class TriviaCommands:
    def __init__(self, client: Client):
        self.game_handler = TriviaPlayer(client)
        self.trivia_creator = TriviaCreator(client)
        self.trivia_updater = TriviaUpdater(client)
        
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
        
    async def handle_list_trivias(self, message: Message) -> None:
        """Route list trivias command to updater"""
        await self.trivia_updater.handle_list_trivias(message)
        
    async def handle_update_trivia(self, message: Message) -> None:
        """Route update trivia command to updater"""
        await self.trivia_updater.handle_update_trivia(message)