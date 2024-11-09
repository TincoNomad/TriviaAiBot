from discord import Message
from ..game_state import GameState, PlayerGame
from ..trivia_game import TriviaGame
from ..utils.logging_bot import command_logger
from asyncio import TimeoutError
import discord
import asyncio

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
        print(f"DEBUG Theme - Available themes: {theme_list}")
        print(f"DEBUG Theme - Theme choices in game: {self.trivia_game.theme_choices}")
        
        await message.author.send(f"Select a theme by number:\n{theme_list}")
        
        def check(m):
            return (
                m.author == message.author and 
                m.content.isdigit() and 
                int(m.content) in self.trivia_game.theme_choices
            )
        
        try:
            response = await self.client.wait_for('message', timeout=30.0, check=check)
            print(f"DEBUG Theme - Raw user response: {response.content}")
            theme_num = int(response.content)
            print(f"DEBUG Theme - User selected theme number: {theme_num}")
            theme_data = self.trivia_game.theme_choices[theme_num]
            theme_id = theme_data['id']
            print(f"DEBUG Theme - Selected theme_id: {theme_id}")
            print(f"DEBUG Theme - GameState before update: {self.game_state.user_selections}")
            
            # Inicializar o actualizar las selecciones del usuario
            if message.author.id not in self.game_state.user_selections:
                self.game_state.user_selections[message.author.id] = {}
            
            # Guardar el theme_id
            self.game_state.user_selections[message.author.id]['theme'] = theme_id
            print(f"DEBUG Theme - GameState after update: {self.game_state.user_selections}")
            
            return theme_id
        except TimeoutError:
            raise TimeoutError("Theme selection timed out")

    async def _handle_difficulty_selection(self, message: Message):
        """Handles the difficulty selection step"""
        _, difficulty_list = await self.trivia_game.get_available_options()
        print(f"DEBUG Difficulty - Available difficulties: {difficulty_list}")
        print(f"DEBUG Difficulty - Difficulty choices in game: {self.trivia_game.difficulty_choices}")
        
        await message.author.send(f"Select difficulty by number:\n{difficulty_list}")
        
        async def handle_response():
            def check(m):
                print(f"DEBUG Difficulty - Checking message: {m.content}")
                print(f"DEBUG Difficulty - Difficulty choices: {self.trivia_game.difficulty_choices}")
                if not (m.author == message.author and m.content.isdigit()):
                    return False
                num = int(m.content)
                return num in [1, 2, 3]
            
            while True:
                try:
                    response = await self.client.wait_for('message', timeout=30.0, check=check)
                    print(f"DEBUG Difficulty - User selected difficulty: {response.content}")
                    difficulty_level = int(response.content)
                    
                    # Guardar la dificultad seleccionada
                    await self.trivia_game.set_difficulty(difficulty_level)
                    
                    # Actualizar el estado del juego
                    user_selections = self.game_state.user_selections.get(message.author.id, {})
                    user_selections["difficulty"] = difficulty_level
                    self.game_state.user_selections[message.author.id] = user_selections
                    
                    print(f"DEBUG Difficulty - GameState after update: {self.game_state.user_selections}")
                    return difficulty_level
                except TimeoutError:
                    raise TimeoutError("Difficulty selection timed out")
                except asyncio.TimeoutError:
                    raise TimeoutError("Difficulty selection timed out")
        
        try:
            return await handle_response()
        except ValueError:
            await message.author.send("Invalid difficulty. Please select 1, 2, or 3.")
            return await handle_response()

    async def _handle_trivia_selection(self, message: Message):
        """Handles the trivia selection step"""
        user_selections = self.game_state.user_selections.get(message.author.id, {})
        print(f"DEBUG Trivia - Current user selections: {user_selections}")
        print(f"DEBUG Trivia - Full game state: {self.game_state.user_selections}")
        
        theme_id = user_selections.get("theme")
        difficulty_level = user_selections.get("difficulty")
        print(f"DEBUG Trivia - Retrieved theme_id: {theme_id}")
        print(f"DEBUG Trivia - Retrieved difficulty: {difficulty_level}")
        
        print(f"DEBUG Commands - Trivia selection with theme={theme_id}, difficulty={difficulty_level}")
        print(f"DEBUG Commands - User selections: {user_selections}")
        
        if not theme_id or not difficulty_level:
            print("DEBUG Commands - Missing theme or difficulty")
            raise ValueError("Theme or difficulty not selected")
        
        try:
            print(f"DEBUG Trivia - Calling get_trivia with theme={theme_id}, diff={difficulty_level}")
            trivia_list, count = await self.trivia_game.get_trivia(theme_id, difficulty_level)
            print(f"DEBUG Trivia - Got response: {trivia_list}, count={count}")
        except Exception as e:
            print(f"DEBUG Commands - Error getting trivia: {e}")
            raise
        
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
            print(f"DEBUG Trivia - Raw user response: {response.content}")
            print(f"DEBUG Trivia - Response type: {type(response.content)}")
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
                print(f"DEBUG Questions - Raw user response: {response.content}")
                print(f"DEBUG Questions - Response type: {type(response.content)}")
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
        pass
