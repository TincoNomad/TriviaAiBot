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
            
        async with self.trivia_game.api_client:
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
                await message.channel.send("🙈 Oops, this is embarrassing, but we have a problem. Let's play later, Shall we?")
                self._cleanup_game(user_id)

    async def _handle_game_start(self, message: Message):
        await message.author.send("Welcome to the trivia game! Type 'go' to start.")
        
        try:
            def check(m):
                return m.author == message.author and m.content.lower() == 'go'
            
            await self.client.wait_for('message', timeout=30.0, check=check)
            await message.channel.send("```orange\n------Hey!! Trivia time!---------\n```")
            await message.channel.send("""
```orange
-------------------
Game Time!!!
-------------------
```                                   """)

            await message.channel.send(
            "The game will start soon. There will be 5 questions about a Platzi course. "
            "You'll have 30 seconds to read each question and 10 seconds to respond after the warning. "
            "Each correct answer is worth 10 points!"
            )
            await message.channel.send("Starting in 3 ⏳")
        except TimeoutError:
            await message.author.send("I understand, it's not time to play yet. We'll play another time! 😃")
            raise

    async def _handle_questions(self, message: Message):
        """Handles the questions flow"""
        game = self.game_state.active_games[message.author.id]
        
        if not game.selected_trivia:
            raise ValueError("No trivia selected")
        
        try:
            # Obtener identificador del canal de manera segura
            if isinstance(message.channel, (discord.TextChannel, discord.Thread)):
                channel_identifier = message.channel.name
            else:
                # Para DMs y otros tipos de canales, usar una combinación de tipo y ID
                channel_type = type(message.channel).__name__
                channel_identifier = f"{channel_type}-{message.channel.id}"
            
            username = message.author.name
            
            # Crear el leaderboard al inicio del juego
            await self.trivia_game.api_client.create_leaderboard(
                discord_channel=channel_identifier,
                username=username
            )
            
            # Obtener preguntas
            trivia_id = next(
                trivia["id"] for trivia in self.trivia_game.current_trivia 
                if trivia["title"] == game.selected_trivia
            )
            questions = await self.trivia_game.get_trivia_questions(trivia_id)
            game.total_questions = len(questions)
            
            while game.current_question < game.total_questions:
                players = []
                
                question, correct_answer, points, options = self.trivia_game.get_question(
                    questions,
                    game.current_question
                )
                
                await message.channel.send("```orange\n------------ QUESTION -------------\n```")
                await message.channel.send(f"Question {game.current_question + 1}: Read the question, you have 30 seconds")
                await message.channel.send(question)
                
                # Mostrar las opciones de respuesta
                if options:
                    options_text = "\n".join(options)
                    await message.channel.send(f"```\nOptions:\n{options_text}\n```")
                else:
                    await message.channel.send("Error: No options available for this question")
                    game.current_question += 1
                    continue
                
                def check(m):
                    return (
                        m.content.isdigit() and 
                        1 <= int(m.content) <= 4
                    )
                
                try:
                    while True:
                        response = await self.client.wait_for('message', timeout=30.0, check=check)
                        player_info = f"{response.author.name}#{response.author.discriminator}"
                        
                        if player_info not in players:
                            players.append(player_info)
                            if int(response.content) == correct_answer:
                                game.current_score += points
                                await message.channel.send(f"Correct! {response.author.name}, you won {points} points 🥳\n\n")
                                await self.trivia_game.api_client.update_score(
                                    name=response.author.name,
                                    points=points,
                                    discord_channel=channel_identifier
                                )
                                break
                            else:
                                await message.channel.send(f"Uh no {response.author.name}, that's not the answer 😞\n\n")
                                await self.trivia_game.api_client.update_score(
                                    name=response.author.name,
                                    points=0,
                                    discord_channel=channel_identifier
                                )
                        else:
                            await message.channel.send(f"{response.author.name}, You can only try once 🙈")
                            
                    game.current_question += 1
                        
                except TimeoutError:
                    await message.channel.send("ohhh, it seems no one guessed this 😔. Well, let's move on to the next one 💪🏽")
                    game.current_question += 1

            # End game
            await message.channel.send("""
End of the Game. Thanks for participating 💚
                                   """)
            await message.channel.send("It was very fun 💃🕺 Congratulations!")
            
            try:
                # Obtener y mostrar el leaderboard final
                leaderboard = await self.trivia_game.api_client.get_leaderboard(
                    discord_channel=channel_identifier
                )
                
                # Formatear el leaderboard de manera más legible
                if isinstance(leaderboard, list):
                    formatted_scores = "\n".join(
                        f"{player['name']}: {player['points']} points" 
                        for player in leaderboard
                    )
                    await message.channel.send("🏆 Final Leaderboard:")
                    await message.channel.send(f"```\n{formatted_scores}\n```")
                else:
                    await message.channel.send("No scores available in the leaderboard!")
            except Exception as e:
                command_logger.error(f"Error getting leaderboard: {e}")
                await message.channel.send("Error getting the leaderboard. Please try again later.")
            
            # Mostrar el link del curso si está disponible
            url = self.trivia_game.get_link(game.selected_trivia)
            if url:
                await message.channel.send(f"The theme of this game was the course {url}")
        except Exception as e:
            command_logger.error(f"Error getting trivia: {e}")
            await message.channel.send("🙈 Oops, this is embarrassing, but we have a problem. Let's play later, Shall we?")
            raise

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
            theme_num = int(response.content)
            theme_data = self.trivia_game.theme_choices[theme_num]
            theme_id = theme_data['id']
            
            # Inicializar o actualizar las selecciones del usuario
            if message.author.id not in self.game_state.user_selections:
                self.game_state.user_selections[message.author.id] = {}
            
            # Guardar el theme_id
            self.game_state.user_selections[message.author.id]['theme'] = theme_id
            await message.channel.send("2 ⏳")

            return theme_id
        except TimeoutError:
            raise TimeoutError("Theme selection timed out")

    async def _handle_difficulty_selection(self, message: Message):
        """Handles the difficulty selection step"""
        _, difficulty_list = await self.trivia_game.get_available_options()

        await message.author.send(f"Select difficulty by number:\n{difficulty_list}")
        
        async def handle_response():
            def check(m):
                if not (m.author == message.author and m.content.isdigit()):
                    return False
                num = int(m.content)
                return num in [1, 2, 3]
            
            while True:
                try:
                    response = await self.client.wait_for('message', timeout=30.0, check=check)
                    difficulty_level = int(response.content)
                    
                    # Guardar la dificultad seleccionada
                    await self.trivia_game.set_difficulty(difficulty_level)
                    
                    # Actualizar el estado del juego
                    user_selections = self.game_state.user_selections.get(message.author.id, {})
                    user_selections["difficulty"] = difficulty_level
                    self.game_state.user_selections[message.author.id] = user_selections
                    await message.channel.send("1 ⏳...")
                    
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
        try:
            user_selections = self.game_state.user_selections.get(message.author.id, {})

            theme_id = user_selections.get("theme")
            difficulty_level = user_selections.get("difficulty")
            
            if not theme_id or not difficulty_level:
                raise ValueError("Theme or difficulty not selected")
            
            try:
                trivia_list, count = await self.trivia_game.get_trivia(theme_id, difficulty_level)
            except Exception as e:
                command_logger.error(f"Error getting trivia: {e}")
                await message.channel.send("🙈 Oops, this is embarrassing, but we have a problem. Let's play later, Shall we?")
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
                selected_index = int(response.content) - 1
                selected_trivia = self.trivia_game.current_trivia[selected_index]["title"]
                self.game_state.active_games[message.author.id].selected_trivia = selected_trivia
            except TimeoutError:
                raise TimeoutError("Trivia selection timed out")

        except Exception as e:
            command_logger.error(f"Error getting trivia: {e}")
            await message.channel.send("🙈 Oops, this is embarrassing, but we have a problem. Let's play later, Shall we?")
            raise

    def _cleanup_game(self, user_id: int):
        """Cleans up the game state when it ends or there's an error"""
        if user_id in self.game_state.active_games:
            del self.game_state.active_games[user_id]
        if user_id in self.game_state.user_selections:
            del self.game_state.user_selections[user_id]

    async def handle_score(self, message: Message):
        try:
            channel_identifier = message.channel.name if isinstance(
                message.channel, (discord.TextChannel, discord.Thread)
            ) else f"{type(message.channel).__name__}-{message.channel.id}"
            
            leaderboard = await self.trivia_game.api_client.get_leaderboard(
                discord_channel=channel_identifier
            )
            
            if not leaderboard:
                await message.channel.send("No scores yet!")
                return
            
            # Asumiendo que leaderboard es un diccionario con una lista de scores
            scores = leaderboard.get('scores', [])  # Ajusta esto según la estructura real de tu respuesta
            
            formatted_scores = "\n".join(
                f"{score['name']}, {score['points']} points" 
                for score in scores
            )
            
            await message.channel.send(f"🏆 Leaderboard:\n```\n{formatted_scores}\n```")
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
