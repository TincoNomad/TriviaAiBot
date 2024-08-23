import asyncio
import discord
from .utils import logger, School, Difficulty, TIMEOUT_DURATION, MAX_QUESTIONS
from .data_handlers import get_score, update_score
from .trivia_game import TriviaGame


# Main Discord Bot class
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trivia_game = TriviaGame()
        self.schools = """
        Choose a school:
        1- Developing
        2- Data/M-Learning
        3- Marketing
        4- Design
        5- Soft Skills
        6- Business
        7- Finanzas
        8- Digital Content
        9- Startup
        10- English      
        """
        self.difficulty = """
        Choose a difficulty:
        1- Beginner
        2- Intermediate
        3- Advanced
        """

    # Confirm bot connection
    async def on_ready(self):
        logger.info(f"We are connected as {self.user}")

    # Handle incoming messages
    async def on_message(self, message):
        if message.author == self.user:
            return

        # Display the current leaderboard
        async def score():
            leaderboard = get_score()
            await message.channel.send(leaderboard)

        # Handle the "$puntaje" command to show scores
        if message.content == "$puntaje":
            await score()

        # Handle the "$cursos" command to list available courses
        if message.content == "$cursos":
            try:
                await message.author.send(self.schools)

                try:
                    respuesta = await self.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
                except asyncio.TimeoutError:
                    return await message.author.send(
                        "Ups, you took too long to choose an option 😄"
                        + "\n"
                        + 'Write "$cursos" in the channel, one more time, and try again 😊'
                    )

                school_option = respuesta.content
                await message.author.send(self.difficulty)
                try:
                    respuesta = await self.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
                except asyncio.TimeoutError:
                    return await message.author.send(
                        "Ups, you took too long to choose an option 😄"
                        + "\n"
                        + 'Write "$cursos" in the channel one more time, and try again 😊'
                    )

                difficulty_level = respuesta.content
                # get_course(school_option, difficulty_level)

                course, numero = self.trivia_game.get_course(school_option, difficulty_level)

                if numero != 0:
                    await message.author.send(course)
                    await message.author.send(
                        "`If you don't see the course you're looking for, you can ask for it to be added to the game 😊`"
                    )
                    try:
                        respuesta = await self.wait_for(
                            "message", check=self.options, timeout=60
                        )
                    except asyncio.TimeoutError:
                        return await message.author.send(
                            '`If you need more time, you can write "$cursos" in the channel again 😊`'
                        )

            except discord.errors.Forbidden:
                await message.channel.send("No puedo enviarte un mensaje directo. Por favor, verifica tus configuraciones de privacidad.")
            except Exception as e:
                await message.channel.send(f"Ocurrió un error inesperado: {e}")

        # Handle the "$trivia" command to start the game
        if message.content == "$trivia":
            logger.info(f"Usuario {message.author} inició un juego de trivia")
            await message.channel.send(
                f"hello, {message.author.mention}. I sent you a message by DM 😊"
            )
            await message.author.send(
                """We're about to start the Platzi trivia game 🥳.
If it's really time to play, write "go" to choose the theme of the Trivia. If it's not time to play, don't write anything or write anything else 😜"""
            )

            try:
                decision_to_start = await self.wait_for(
                    "message", check=self.start_game, timeout=TIMEOUT_DURATION
                )
            except asyncio.TimeoutError:
                return await message.author.send(
                    "I understand, it's not time to play yet, no problem 😉, we'll play another time 😃"
                )

            if str.lower(decision_to_start.content) == "go":
                logger.info(f"Usuario {message.author} comenzó el juego de trivia")
                await message.channel.send("------Hey!!Trivia time!---------")
                await message.channel.send("""
```
-------------------
  Game Time!!!  
-------------------         
```              
            
            """)
                await message.channel.send("""Soon the game will start, there will be 5 questions and the theme will be one of the Platzi courses, you'll have 30 seconds to read the question and then after the warning, 10 seconds to respond. 
If no one responds, we'll move on to the next question. When someone responds correctly, the next question will appear and they'll earn 10 points.""")
                await message.channel.send("We'll start in 3 ⏳")

                # Cargar datos del juego
                try:
                    await self.trivia_game.fetch_game_data()
                except Exception as e:
                    await message.channel.send(f"Lo siento, ocurrió un error al cargar los datos del juego: {e}")
                    return

                # Collect game parameters (school and difficulty)
                try:
                    school_option = await self.get_school_option(message)
                    if school_option is None:
                        return await message.channel.send("Ups, esto es vergonzoso 🙈, parece que tuvimos un problema con la selección de la escuela, pero no te preocupes, ¡jugaremos pronto 😄!")

                    difficulty_level = await self.get_difficulty_level(message)
                    if difficulty_level is None:
                        return await message.channel.send("Ups, esto es vergonzoso 🙈, parece que tuvimos un problema con la selección de la dificultad, pero no te preocupes, ¡jugaremos pronto 😄!")

                    course, numero = self.trivia_game.get_course(school_option, difficulty_level)
                    if numero == 0:
                        await message.author.send(course)
                        await message.author.send(
                            "you can go to the game admin to add it and come back to play again 😃"
                        )
                        return

                    await message.author.send("Choose a course:")
                    await message.author.send(course)
                    await message.channel.send("... 1 ⏳")

                    try:
                        respuesta = await self.wait_for(
                            "message", check=self.options, timeout=TIMEOUT_DURATION
                        )
                    except asyncio.TimeoutError:
                        return await message.channel.send("""
Ups, you took too long 😄, if you still don't know about which course to make the game, no problem, review 
the list and then come back with the $trivia command""")

                    if int(respuesta.content) <= numero:
                        position = int(respuesta.content) - 1
                        selected_course = self.trivia_game.game_data[position]["title"]
                        await message.author.send(
                            "Success in choosing the course. We'll start in 10 seconds 🥳"
                        )
                    else:
                        await message.author.send(
                            "You chose an incorrect option, please try again 😊"
                        )
                        return

                    # Game action: ask questions and handle answers
                    question_counter = 0
                    while question_counter <= MAX_QUESTIONS - 1:
                        await self.game(message, selected_course, question_counter)
                        question_counter += 1
                    logger.info(f"Juego de trivia finalizado para el usuario {message.author}")
                    await message.channel.send("""
```
   End of the Game. Thanks for participating 💚          
``` 
                    """)
                    await message.channel.send(
                        "It was very fun 💃🕺 Congratulations!\nFinal Score: "
                    )
                    await score()
                    url = self.trivia_game.getLink(selected_course)
                    await message.channel.send(f"The theme of this game was the course {url}")

                except Exception as e:
                    logger.error(f"Error inesperado durante el juego: {e}")
                    await message.channel.send(f"Lo siento, ocurrió un error inesperado: {e}. Por favor, intenta iniciar el juego de nuevo.")
                    return
            else:
                return await message.author.send(
                    "I understand, it's not time to play yet, no problem 😉, we'll play another time 😃"
                )

    @staticmethod
    def check(message):
        return message.content.isdigit()

    @staticmethod
    def options(message):
        return message.content.isdigit()

    @staticmethod
    def start_game(message):
        return message.content

    async def get_school_option(self, message):
        await message.author.send(self.schools)
        try:
            respuesta = await self.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
            school_option = int(respuesta.content)
            if school_option not in [school.value for school in School]:
                await message.author.send("Opción inválida. Por favor, elige un número entre 1 y 10.")
                return None
            return school_option
        except asyncio.TimeoutError:
            await message.author.send("Ups, tardaste demasiado en elegir una opción 😄\nEscribe '$trivia' en el canal una vez más e inténtalo de nuevo 😊")
            return None

    async def get_difficulty_level(self, message):
        await message.author.send(self.difficulty)
        try:
            respuesta = await self.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
            difficulty_level = int(respuesta.content)
            if difficulty_level not in [diff.value for diff in Difficulty]:
                await message.author.send("Opción inválida. Por favor, elige un número entre 1 y 3.")
                return None
            return difficulty_level
        except asyncio.TimeoutError:
            await message.author.send("Ups, tardaste demasiado en elegir una opción 😄\nEscribe '$trivia' en el canal una vez más e inténtalo de nuevo 😊")
            return None

    async def game(self, message, selected_course, question_counter):
        try:
            logger.info(f"Iniciando pregunta {question_counter + 1} para el curso {selected_course}")
            await asyncio.sleep(10)
            await message.channel.send("```\n------------ QUESTION -------------\n```")

            question, answer, points = self.trivia_game.get_question(selected_course, question_counter)

            if question == "Error al obtener la pregunta" or question == "Error al procesar los datos de la pregunta":
                await message.channel.send(f"Lo siento, hubo un problema al obtener la pregunta: {question}")
                return

            await message.channel.send("----------------------------------\nRead the question, you have 30 seconds")
            await message.channel.send(question)

            await self.attempt(message, answer, points)
        except Exception as e:
            logger.error(f"Error durante el juego: {e}")
            await message.channel.send(f"Lo siento, ocurrió un error inesperado durante el juego: {e}")

    async def attempt(self, message, answer, points):
        players = []

        try:
            while True:
                try:
                    guess = await self.wait_for("message", check=self.check, timeout=TIMEOUT_DURATION)
                    logger.info(f"Usuario {guess.author} intentó responder")
                except asyncio.TimeoutError:
                    logger.info("Tiempo agotado para responder la pregunta")
                    return await message.channel.send("ohhh, it seems no one guessed this 😔. Well, let's move on to the next one 💪🏽")

                player_info = f"{guess.author.name}{guess.author.discriminator}"

                if player_info not in players:
                    players.append(player_info)
                    if int(guess.content) == answer:
                        await message.channel.send(f"Correct! {guess.author.name}, you won {points} points 🥳\n\n")
                        update_score(guess.author, points)
                        break
                    else:
                        await message.channel.send(f"Uh no {guess.author.name}, that's not the answer 😞\n\n")
                        update_score(guess.author, 0)
                else:
                    await message.channel.send(f"{guess.author.name}, You can only try once 🙈")
        except Exception as e:
            logger.error(f"Error durante el intento de respuesta: {e}")
            await message.channel.send(f"Lo siento, ocurrió un error inesperado durante el intento de respuesta: {e}")