from discord import Message
from ..game_state import GameState, PlayerGame
from ..trivia_game import TriviaGame
from ..utils.logging_bot import command_logger
from asyncio import TimeoutError
import discord

class TriviaCommands:
    def __init__(self, client: discord.Client):
        self.trivia_game = TriviaGame()
        self.game_state = GameState()
        self.client = client
        
    async def handle_trivia(self, message: Message) -> None:
        user_id = message.author.id
        channel_id = message.channel.id
        
        if user_id in self.game_state.active_games:
            await message.author.send("You already have an active game!")
            return
            
        try:
            # Inicializar el juego
            await self.trivia_game.initialize()
            
            # Obtener opciones
            theme_list, difficulty_list = await self.trivia_game.get_available_options()
            
            # Crear estado del jugador
            self.game_state.active_games[user_id] = PlayerGame(
                channel_id=channel_id,
                current_score=0,
                current_question=0
            )
            
            # Flujo del juego
            await self._handle_game_start(message)
            await self._handle_theme_selection(message)
            await self._handle_difficulty_selection(message)
            await self._handle_trivia_selection(message)
            await self._handle_questions(message)
            
        except TimeoutError:
            await message.author.send("Timeout. Try again with $trivia")
            self._cleanup_game(user_id)
        except Exception as e:
            command_logger.error(f"Error in trivia command: {e}")
            await message.author.send("An error occurred. Please try again.")
            self._cleanup_game(user_id)

    async def _handle_game_start(self, message: Message):
        await message.author.send("Welcome to the trivia game! Type 'go' to start.")
        
        def check(m):
            return m.author == message.author and m.content.lower() == 'go'
        
        await self.client.wait_for('message', timeout=30.0, check=check)

    async def _handle_theme_selection(self, message: Message):
        """Handles the theme selection step"""
        theme_list, _ = await self.trivia_game.get_available_options()
        await message.author.send(f"Select a theme by number:\n{theme_list}")
        
        def check(m):
            return (
                m.author == message.author and 
                m.content.isdigit() and 
                int(m.content) in self.trivia_game.theme_choices
            )
        
        try:
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            theme_id = self.trivia_game.theme_choices[int(response.content)]
            self.game_state.user_selections[message.author.id] = {"theme": theme_id}
            return theme_id
        except TimeoutError:
            raise TimeoutError("Theme selection timed out")

    async def _handle_difficulty_selection(self, message: Message):
        """Handles the difficulty selection step"""
        _, difficulty_list = await self.trivia_game.get_available_options()
        await message.author.send(f"Select difficulty by number:\n{difficulty_list}")
        
        def check(m):
            return (
                m.author == message.author and 
                m.content.isdigit() and 
                int(m.content) in self.trivia_game.difficulty_choices
            )
        
        try:
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            difficulty_level = int(response.content)
            self.game_state.user_selections[message.author.id]["difficulty"] = difficulty_level
            return difficulty_level
        except TimeoutError:
            raise TimeoutError("Difficulty selection timed out")

    async def _handle_trivia_selection(self, message: Message):
        """Handles the trivia selection step"""
        user_selections = self.game_state.user_selections.get(message.author.id, {})
        theme_id = user_selections.get("theme")
        difficulty_level = user_selections.get("difficulty")
        
        if not theme_id or not difficulty_level:
            raise ValueError("Theme or difficulty not selected")
        
        trivia_list, count = await self.trivia_game.get_trivia(theme_id, difficulty_level)
        
        if count == 0:
            await message.author.send("No trivias available for this combination")
            raise ValueError("No trivias available")
            
        await message.author.send(f"Select a trivia by number:\n{trivia_list}")
        
        def check(m):
            return (
                m.author == message.author and 
                m.content.isdigit() and 
                1 <= int(m.content) <= count
            )
        
        try:
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            selected_index = int(response.content) - 1
            selected_trivia = self.trivia_game.current_trivia[selected_index]["title"]
            self.game_state.active_games[message.author.id].selected_trivia = selected_trivia
        except TimeoutError:
            raise TimeoutError("Trivia selection timed out")

    async def _handle_questions(self, message: Message):
        """Handles the questions flow"""
        game = self.game_state.active_games[message.author.id]
        
        if not game.selected_trivia:
            raise ValueError("No trivia selected")
            
        while game.current_question < game.total_questions:
            question, correct_answer, points = self.trivia_game.get_question(
                game.selected_trivia,
                game.current_question
            )
            
            await message.author.send(f"Question {game.current_question + 1}: {question}")
            
            def check(m):
                return (
                    m.author == message.author and 
                    m.content.isdigit() and 
                    1 <= int(m.content) <= 4
                )
            
            try:
                response = await self.client.wait_for('message', timeout=30.0, check=check)
                if int(response.content) == correct_answer:
                    game.current_score += points
                    await message.author.send(f"Correct! +{points} points")
                else:
                    await message.author.send(f"Wrong! The correct answer was {correct_answer}")
                
                game.current_question += 1
                
            except TimeoutError:
                raise TimeoutError("Question answering timed out")

    def _cleanup_game(self, user_id: int):
        """Cleans up the game state when it ends or there's an error"""
        if user_id in self.game_state.active_games:
            del self.game_state.active_games[user_id]
        if user_id in self.game_state.user_selections:
            del self.game_state.user_selections[user_id]

    async def handle_score(self, message: Message):
        """Handles the $score command"""
        try:
            leaderboard = await self.trivia_game.api_client.get_leaderboard()
            await message.channel.send(f"Score table:\n{leaderboard}")
        except Exception as e:
            command_logger.error(f"Error in score command: {e}")
            await message.channel.send("Error getting the score table.")

    async def handle_courses(self, message: Message):
        """Handles the $courses command"""
        try:
            theme_list, difficulty_list = await self.trivia_game.get_available_options()
            await message.channel.send(f"Available themes:\n{theme_list}")
            await message.channel.send(f"Available difficulties:\n{difficulty_list}")
        except Exception as e:
            command_logger.error(f"Error in courses command: {e}")
            await message.channel.send("Error getting the list of courses.")

    async def handle_game_response(self, message: Message) -> None:
        """Handles responses during an active game"""
        user_id = message.author.id
        game = self.game_state.active_games.get(user_id)
        
        if not game:
            return
            
        # Si el usuario está en medio de una pregunta, la respuesta será manejada por _handle_questions
        # Si el usuario está seleccionando tema/dificultad/trivia, será manejado por los respectivos handlers
        # No necesitamos hacer nada adicional aquí porque wait_for() en los otros métodos ya maneja las respuestas
        pass
