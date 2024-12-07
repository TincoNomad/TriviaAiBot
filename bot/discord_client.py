import discord
from .utils.logging_bot import bot_logger
from .commands.trivia_commands import TriviaCommands


# Main Discord Bot class
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trivia_commands = TriviaCommands(self)

    # Confirm bot connection
    async def on_ready(self):
        bot_logger.info(f"We are connected as {self.user}")

    # Handle incoming messages
    async def on_message(self, message):
        if message.author == self.user:
            return

        user_id = message.author.id
        
        # Manejar comandos principales
        if message.content.startswith('$'):
            if message.content.startswith('$trivia'):
                await self.trivia_commands.handle_trivia(message)
            elif message.content.startswith('$score'):
                await self.trivia_commands.handle_score(message)
            elif message.content.startswith('$themes'):
                await self.trivia_commands.handle_themes(message)
            elif message.content.startswith('$stopgame'):
                await self.trivia_commands.handle_stop_game(message)
            elif message.content.startswith('$create'):
                await self.trivia_commands.handle_create_trivia(message)
        # Manejar respuestas del juego
        elif user_id in self.trivia_commands.game_state.active_games:
            await self.trivia_commands.handle_game_response(message)
