from discord import Message
from ..game_state import GameState, PlayerGame
from ..trivia_game import TriviaGame
from ..utils.logging_bot import command_logger
from asyncio import TimeoutError
import discord
import asyncio
from typing import List, Dict, Any
from api.django import TRIVIA_URL
import json

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
                # Initialize game
                await self.trivia_game.initialize()
                
                # Get options
                theme_list, difficulty_list = await self.trivia_game.get_available_options()
                
                # Create player state
                self.game_state.active_games[user_id] = PlayerGame(
                    channel_id=channel_id,
                    current_score=0,
                    current_question=0
                )
                
                # Game flow
                await self._handle_game_start(message)
                await self._handle_theme_selection(message)
                await self._handle_difficulty_selection(message)
                await self._handle_trivia_selection(message)
                await self._handle_questions(message)
                
            except TimeoutError:
                await message.author.send("Timeout. Try again with $trivia")
                await message.channel.send("🙈 Oops, this is embarrassing, but we have a problem. Let's play later, Shall we?")
                self._cleanup_game(user_id)
            except Exception as e:
                command_logger.error(f"Error in trivia command: {e}")
                await message.author.send("An error occurred. Please try again.")
                await message.channel.send("🙈 Oops, something went wrong. Let's try again later!")
                self._cleanup_game(user_id)
            finally:
                # Ensure game state is cleaned up in all cases
                self._cleanup_game(user_id)

    async def _handle_game_start(self, message: Message):
        await message.author.send("Welcome to the trivia game! Type 'go' to start.")
        
        try:
            def check(m):
                return m.author == message.author and m.content.lower() == 'go'
            
            await self.client.wait_for('message', timeout=30.0, check=check)
            await message.channel.send("```orange\n------Hey!! Trivia it's about to start!---------\n```")
            await message.channel.send("""
```orange
-------------------
Game Time!!!
-------------------
```                                   """)

            await message.channel.send(
"""The game will start soon. There will be a minimum of 3 questions about different subjects.
Each correct answer is worth 10 points!
Ready!? 🚀"""
            )
        except TimeoutError:
            await message.author.send("I understand, it's not time to play yet. We'll play another time! 😃")
            raise

    async def _handle_questions(self, message: Message):
        """Handles the questions flow"""
        game = self.game_state.active_games[message.author.id]
        
        if not game.selected_trivia:
            raise ValueError("No trivia selected")
        
        try:
            # Enviar mensaje privado y esperar 5 segundos antes de comenzar
            await message.author.send("The game will start in 5 seconds")
            await asyncio.sleep(5)
            
            # Get channel identifier safely
            if isinstance(message.channel, (discord.TextChannel, discord.Thread)):
                channel_identifier = message.channel.name
            else:
                # For DMs and other channel types, use a combination of type and ID
                channel_type = type(message.channel).__name__
                channel_identifier = f"{channel_type}-{message.channel.id}"
            
            username = message.author.name
            
            # Create leaderboard at the beginning of the game
            await self.trivia_game.api_client.create_leaderboard(
                discord_channel=channel_identifier,
                username=username
            )
            
            # Get questions
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
                await message.channel.send(f"Question {game.current_question + 1}")
                await message.channel.send(f"```\n{question}\n```")
                
                if options:
                    options_text = "\n".join(options)
                    await message.channel.send(f"```\nOptions:\n{options_text}\n```")
                    num_options = len(options)  # Obtener el número de opciones disponibles
                else:
                    await message.channel.send("Error: No options available for this question")
                    game.current_question += 1
                    continue
                
                def check(m):
                    # Ignore messages from the bot itself
                    if m.author == self.client.user:
                        return False
                    
                    # Verify message is in the correct channel
                    if m.channel != message.channel:
                        return False
                    
                    # If not a number, ignore
                    if not m.content.isdigit():
                        asyncio.create_task(message.channel.send(
                            f"{m.author.name}, please enter a number between 1 and {num_options} 🤔"
                        ))
                        return False
                    
                    # If number is out of range, ignore
                    num = int(m.content)
                    if not (1 <= num <= num_options):
                        asyncio.create_task(message.channel.send(
                            f"{m.author.name}, the number must be between 1 and {num_options} 🎯"
                        ))
                        return False
                    
                    return True
                
                try:
                    while True:
                        response = await self.client.wait_for('message', timeout=30.0, check=check)
                        player_info = f"{response.author.name}#{response.author.discriminator}"
                        
                        if player_info not in players:
                            players.append(player_info)
                            if int(response.content) == correct_answer:
                                game.current_score += points
                                await message.channel.send(f"Correct! {response.author.name}, you won {points} points \n\n")
                                await self.trivia_game.api_client.update_score(
                                    name=response.author.name,
                                    points=points,
                                    discord_channel=channel_identifier
                                )
                                break
                            else:
                                await message.channel.send(f"Uh no {response.author.name}, that's not the answer 😞\n\n")
                        else:
                            await message.channel.send(f"{response.author.name}, You can only try once 🙈")
                            
                    game.current_question += 1
                        
                except TimeoutError:
                    await message.channel.send("ohhh, it seems no one guessed this 😔. Well, let's move on to the next one 💪🏽")
                    game.current_question += 1

            # End game messages
            await message.channel.send(
                "```orange\nEnd of the Game. Thanks for participating 🧡\n```"
            )
            await message.channel.send("It was very fun 💃🕺 Congratulations!")
            
            try:
                # Get and show the final leaderboard
                leaderboard = await self.trivia_game.api_client.get_leaderboard(
                    discord_channel=channel_identifier
                )
                
                # Format the leaderboard in a more readable way
                if isinstance(leaderboard, list):
                    formatted_scores = "\n".join(
                        f"{player['name']}: {player['points']} points" 
                        for player in leaderboard
                    )
                    await message.channel.send("🏆 Final Leaderboard:")
                    await message.channel.send(f"```\n{formatted_scores}\n```")
                else:
                    await message.channel.send("No scores available in the leaderboard!")

                # Agregar mensaje sobre el tema de la trivia
                await message.channel.send(f"This game was about: {game.selected_trivia} 📚")
                
            except Exception as e:
                command_logger.error(f"Error getting leaderboard: {e}")
                await message.channel.send("Error getting the leaderboard. Please try again later.")
            
            # Show course link if available
            url = self.trivia_game.get_link(game.selected_trivia)
            if url:
                await message.channel.send(f"The theme of this game was the course {url}")
        except Exception as e:
            command_logger.error(f"Error getting trivia: {e}")
            await message.channel.send("🙈 Oops, something went wrong. Let's try again later!")
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
            
            if message.author.id not in self.game_state.user_selections:
                self.game_state.user_selections[message.author.id] = {}
            
            self.game_state.user_selections[message.author.id]['theme'] = theme_id
            await message.channel.send("Starting game in 3 ⏳")

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
                    
                    # Save the selected difficulty
                    await self.trivia_game.set_difficulty(difficulty_level)
                    
                    # Update game state
                    user_selections = self.game_state.user_selections.get(message.author.id, {})
                    user_selections["difficulty"] = difficulty_level
                    self.game_state.user_selections[message.author.id] = user_selections
                    await message.channel.send("2 ⏳")
                    
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
                await message.channel.send("🙈 Oops, something went wrong. Let's try again later!")
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
                await message.channel.send("1 ⏳")
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
            
            # Verificar si leaderboard es una lista como en _handle_questions
            if isinstance(leaderboard, list):
                formatted_scores = "\n".join(
                    f"{player['name']}: {player['points']} points" 
                    for player in leaderboard
                )
                await message.channel.send("🏆 Leaderboard:\n```\n{}\n```".format(formatted_scores))
            else:
                await message.channel.send("No scores available in the leaderboard!")
                
        except Exception as e:
            command_logger.error(f"Error in score command: {e}")
            await message.channel.send("Error getting the score table.")

    async def handle_themes(self, message: Message):
        """Handles the $themes command"""
        try:
            theme_list, _ = await self.trivia_game.get_available_options()
            await message.channel.send(f"Available themes:\n{theme_list}")
        except Exception as e:
            command_logger.error(f"Error getting themes: {e}")
            await message.channel.send("Error getting the list of themes.")

    async def handle_game_response(self, message: Message) -> None:
        """Handles responses during an active game"""
        user_id = message.author.id
        game = self.game_state.active_games.get(user_id)
        
        if not game:
            return
        
        # Agregar el comando para acortar el juego
        if message.content.lower() == "$stopgame":
            await self.handle_stop_game(message)
            return
        pass

    async def handle_stop_game(self, message: Message) -> None:
        """Completely ends the current game"""
        user_id = message.author.id
        
        # Verificar si hay un juego activo
        if user_id not in self.game_state.active_games:
            await message.channel.send("There is no active game to end!")
            return
        
        game = self.game_state.active_games[user_id]
        
        # Obtener el canal para mostrar el mensaje final
        channel_identifier = message.channel.name if isinstance(
            message.channel, (discord.TextChannel, discord.Thread)
        ) else f"{type(message.channel).__name__}-{message.channel.id}"
        
        try:
            # Mostrar el resultado final
            await message.channel.send("```orange\nGame ended early.\n```")
            
            # Intentar mostrar el leaderboard final
            try:
                leaderboard = await self.trivia_game.api_client.get_leaderboard(
                    discord_channel=channel_identifier
                )
                
                if isinstance(leaderboard, list):
                    formatted_scores = "\n".join(
                        f"{player['name']}: {player['points']} points" 
                        for player in leaderboard
                    )
                    await message.channel.send("🏆 Final Score:")
                    await message.channel.send(f"```\n{formatted_scores}\n```")
                
                # Mostrar el tema del juego
                await message.channel.send(f"The game was about: {game.selected_trivia} 📚")
                
            except Exception as e:
                command_logger.error(f"Error mostrando puntuación final: {e}")
                await message.channel.send("Could not display final score.")
                
        finally:
            # Limpiar el estado del juego
            self._cleanup_game(user_id)
            await message.channel.send("Thanks for playing! You can start a new game anytime with $trivia")

    async def handle_create_trivia(self, message: Message) -> None:
        """Handles the command to create a new trivia"""
        try:
            # Get title
            await message.author.send("Let's create a new trivia! First, tell me the title:")
            def check_dm(m):
                return m.author == message.author and isinstance(m.channel, discord.DMChannel)
            
            response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
            title = response.content

            # Get theme
            theme_list, _ = await self.trivia_game.get_available_options()
            command_logger.info(f"Available themes list: {theme_list}")
            command_logger.info(f"Theme choices dictionary: {self.trivia_game.theme_choices}")

            await message.author.send(
                f"Available themes:\n{theme_list}\n\n"
                "You can either select a theme by number or type a new theme name."
            )
            response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
            command_logger.info(f"User response: {response.content}")

            # Check if response is a number (existing theme) or text (new theme)
            if response.content.isdigit():
                theme_num = int(response.content)
                command_logger.info(f"Converted to number: {theme_num}")
                command_logger.info(f"Theme choices keys: {self.trivia_game.theme_choices.keys()}")
                command_logger.info(f"Is number in choices?: {theme_num in self.trivia_game.theme_choices}")
                
                if theme_num in self.trivia_game.theme_choices:
                    theme_data = self.trivia_game.theme_choices[theme_num]
                    command_logger.info(f"Theme data found: {theme_data}")
                    theme = theme_data['name']
                    command_logger.info(f"Selected theme name: {theme}")
                else:
                    theme = response.content
                    command_logger.info(f"Theme not found in choices, using as new theme: {theme}")
                    await message.author.send(f"Creating new theme: {theme}")
            else:
                theme = response.content
                command_logger.info(f"Not a number, using as new theme: {theme}")
                await message.author.send(f"Creating new theme: {theme}")

            # Get URL (optional)
            await message.author.send("Would you like to add a URL for this trivia? (yes/no)")
            url = None
            while True:
                response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                if response.content.lower() in ['yes', 'y']:
                    await message.author.send("Please enter the URL:")
                    response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                    url = response.content
                    break
                if response.content.lower() in ['no', 'n']:
                    break
                await message.author.send("Please answer 'yes' or 'no'")

            # Get difficulty
            await message.author.send("Select the difficulty (1-3):")
            def check_difficulty(m):
                return (m.author == message.author and 
                       isinstance(m.channel, discord.DMChannel) and 
                       m.content.isdigit() and 
                       1 <= int(m.content) <= 3)
            
            response = await self.client.wait_for('message', timeout=60.0, check=check_difficulty)
            difficulty = int(response.content)

            # Collect questions
            questions: List[Dict[str, Any]] = []
            await message.author.send("Now let's add the questions. You must add at least 3 questions.")
            await message.author.send("For each question, you'll need to add at least 2 answers.")

            while len(questions) < 3 or (len(questions) < 10):
                # Get question
                await message.author.send(f"\nQuestion #{len(questions) + 1}:")
                await message.author.send("Write the question:")
                response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                question_title = response.content

                # Collect answers for this question
                answers: List[Dict[str, Any]] = []
                await message.author.send("\nNow add the answers. You need at least 2 answers and one must be correct.")

                while len(answers) < 2 or (len(answers) < 4):
                    await message.author.send(f"\nAnswer #{len(answers) + 1}:")
                    await message.author.send("Write the answer:")
                    response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                    answer_title = response.content

                    await message.author.send("Is this the correct answer? (yes/no)")
                    while True:
                        response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                        if response.content.lower() in ['yes', 'y']:
                            is_correct = True
                            break
                        if response.content.lower() in ['no', 'n']:
                            is_correct = False
                            break
                        await message.author.send("Please answer 'yes' or 'no'")

                    answers.append({
                        "answer_title": answer_title,
                        "is_correct": is_correct
                    })

                    if len(answers) >= 2:
                        await message.author.send("Do you want to add another answer? (yes/no)")
                        while True:
                            response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                            if response.content.lower() in ['no', 'n']:
                                break
                            if response.content.lower() in ['yes', 'y']:
                                break
                            await message.author.send("Please answer 'yes' or 'no'")
                        if response.content.lower() in ['no', 'n']:
                            break

                questions.append({
                    "question_title": question_title,
                    "answers": answers
                })

                if len(questions) >= 3:
                    await message.author.send("Do you want to add another question? (yes/no)")
                    while True:
                        response = await self.client.wait_for('message', timeout=60.0, check=check_dm)
                        if response.content.lower() in ['no', 'n']:
                            break
                        if response.content.lower() in ['yes', 'y']:
                            break
                        await message.author.send("Please answer 'yes' or 'no'")
                    if response.content.lower() in ['no', 'n']:
                        break

            trivia_data = {
                "title": title,
                "theme": theme,
                "username": message.author.name,
                "difficulty": difficulty,
                "url": url,
                "questions": questions
            }

            # Agregar log detallado del JSON antes de enviarlo
            command_logger.info("Attempting to create trivia with data:")
            command_logger.info(json.dumps(trivia_data, indent=2))

            # Create trivia using API client
            async with self.trivia_game.api_client:
                try:
                    response = await self.trivia_game.api_client.post(
                        TRIVIA_URL,
                        trivia_data
                    )
                    
                    # Log de la respuesta completa para debug
                    command_logger.info(f"API Response: {json.dumps(response, indent=2)}")
                    
                    if not response:
                        raise ValueError("Empty response from API")
                        
                    # Verificar que la respuesta tenga un ID (lo que indica que se creó exitosamente)
                    if not response.get('id'):
                        error_msg = response.get('error', 'Unknown error')
                        command_logger.error(f"API Error Response: {json.dumps(response, indent=2)}")
                        raise ValueError(f"Error creating trivia: {error_msg}")
                        
                except Exception as e:
                    command_logger.error("Error during trivia creation:")
                    command_logger.error(f"Data sent: {json.dumps(trivia_data, indent=2)}")
                    command_logger.error(f"Exception: {str(e)}")
                    raise

            # Send detailed summary via DM
            summary = [
                "✨ Trivia created successfully! Here's a summary:",
                f"\nTitle: {title}",
                f"Theme: {theme}",
                f"Difficulty: {difficulty}"
            ]
            
            if url:
                summary.append(f"URL: {url}")
                
            summary.append("\nQuestions:")

            for i, q in enumerate(questions, 1):
                summary.append(f"\n{i}. {q['question_title']}")
                for j, a in enumerate(q['answers'], 1):
                    correct = "✅" if a['is_correct'] else "❌"
                    summary.append(f"   {j}. {a['answer_title']} {correct}")

            await message.author.send("\n".join(summary))

        except TimeoutError:
            await message.author.send("Time's up for creating the trivia. Try again with $create_trivia")
        except Exception as e:
            command_logger.error(f"Error creating trivia: {e}")
            await message.author.send("An error occurred while creating the trivia. Please try again.")
