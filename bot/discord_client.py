import discord
from .utils.logging_bot import bot_logger
from .commands.trivia_commands import TriviaCommands


# Main Discord Bot class
class DiscordClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.trivia_commands = TriviaCommands(self)

    # Confirm bot connection
    async def on_ready(self):
        bot_logger.info(f"We are connected as {self.user}")

    # Handle incoming messages
    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        user_id = message.author.id
        content = message.content.lower()

        # Check if it's a command
        if content.startswith('$'):
            command = content[1:]  # Remove the '$'
            
            if command == 'trivia':
                await self.trivia_commands.handle_trivia(message)
            elif command in ['create']:
                await self.trivia_commands.handle_create_trivia(message)
            elif command == 'score':
                await self.trivia_commands.handle_score(message)
            elif command == 'themes':
                await self.trivia_commands.handle_themes(message)
            elif command == 'stopgame':
                await self.trivia_commands.handle_stop_game(message)
            elif command == 'trivias':
                await self.trivia_commands.handle_list_trivias(message)
            elif command == 'update_trivia':
                await self.trivia_commands.handle_update_trivia(message)
        # Check if user is in active game
        elif user_id in self.trivia_commands.game_handler.game_state.active_games:
            await self.trivia_commands.handle_game_response(message)
