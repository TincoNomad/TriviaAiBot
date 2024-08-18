import asyncio
import discord
import requests
import json
from config import LEADERBOARD_URL, SCORE_URL, QUESTION_URL, DISCORD_KEY

# Constants
TIMEOUT_DURATION = 30
MAX_QUESTIONS = 5
POINTS_PER_CORRECT_ANSWER = 10

# Fetch and format the leaderboard data
def get_score():
    try:
        response = requests.get(LEADERBOARD_URL)
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP no exitosos
        json_data = response.json()
        
        if not isinstance(json_data, list):
            raise ValueError("La respuesta no es una lista de diccionarios")
        
        leaderboard = ""
        for id, item in enumerate(json_data, start=1):
            if not isinstance(item, dict):
                raise ValueError("Un elemento de la lista no es un diccionario")
            leaderboard += f"{id} - {item['name']} - {item['points']} Points\n"
        
        return leaderboard if leaderboard else "No hay puntuaciones aún, no se han jugado partidas"
    
    except requests.RequestException as e:
        return f"Error al obtener puntuaciones: {e}"
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        return f"Error al procesar los datos de puntuación: {e}"

# Update player's score in the database
def update_score(name, points):
    url = SCORE_URL
    new_score = {"name": name, "points": points}
    response = requests.post(url, data=new_score)
    return response.status_code


class TriviaGame:
    def __init__(self):
        pass

    def get_course(self, school_option, difficulty_level):
        try:
            response = requests.get(QUESTION_URL)
            response.raise_for_status()
            json_data = response.json()

            course = ""
            numero = 0
            for item in json_data:
                if item["school"] == int(school_option) and item["difficulty"] == int(difficulty_level):
                    numero += 1
                    course += f"\n{numero}-{item['title']}"

            if not course:
                return "Ups, esto es vergonzoso, pero parece que aún no tenemos cursos con esas categorías 😅", 0
            
            return course, numero

        except requests.RequestException as e:
            return f"Error al obtener los cursos: {e}", 0
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return f"Error al procesar los datos de los cursos: {e}", 0

    def get_question(self, selected_course, question_counter):
        try:
            response = requests.get(QUESTION_URL)
            response.raise_for_status()
            json_data = response.json()
            questionOptions = [i["question"] for i in json_data if i["title"] == selected_course]

            question = questionOptions[0][question_counter]["questionTitle"] + "\n\n"
            for id, item in enumerate(questionOptions[0][question_counter]["answer"], start=1):
                question += f"{id}-{item['answerTitle']}\n"

                if item["is_correct"]:
                    answer = id
            return question, answer, POINTS_PER_CORRECT_ANSWER

        except requests.RequestException as e:
            return f"Error al obtener la pregunta: {e}", 0, 0
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return f"Error al procesar los datos de la pregunta: {e}", 0, 0

    def getLink(self, selected_course):
        try:
            response = requests.get(QUESTION_URL)
            response.raise_for_status()
            json_data = response.json()
            for i in json_data:
                if i["title"] == selected_course:
                    return i["url"]
            return "No se encontró el enlace del curso"

        except requests.RequestException as e:
            return f"Error al obtener el enlace del curso: {e}"
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            return f"Error al procesar los datos del curso: {e}"

# Main Discord Bot class
class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trivia_game = TriviaGame()

    # Confirm bot connection
    async def on_ready(self):
        print("We are connected as", self.user)

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

        # Main game logic
        async def game():
            await asyncio.sleep(10)
            await message.channel.send("""
```
------------ QUESTION -------------        
``` 
            """)

            question, answer, points = self.trivia_game.get_question(selected_course, question_counter)
            # question, answer = get_question(selected_course,question_counter)

            await message.channel.send(
                "----------------------------------"
                + "\n"
                + "Read the question, you have 30 seconds"
            )
            await message.channel.send(question)
            # await message.channel.send('----------------------------------'+'\n'+'🕰️ Wait, I'll let you know when to respond 🕰️')

            # def check(message):
            #     return message.author == message.author and message.content.isdigit()

            await attempt(answer, points)

        # Handle player attempts to answer questions
        async def attempt(answer, points):
            players = []

            while True:
                try:
                    guess = await client.wait_for("message", check=self.check, timeout=TIMEOUT_DURATION)
                except asyncio.TimeoutError:
                    return await message.channel.send(
                        "ohhh, it seems no one guessed this 😔. Well, let's move on to the next one 💪🏽"
                    )

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

        # School options for course selection
        schools = """
Choose a school:
1- developing
2- Data/M-Learning
3- marketing
4- design
5- soft skills
6- Business
7- Finanzas
8- digital Content
9- startup
10- english      
        
        """

        # Difficulty options for course selection
        difficulty = """
Choose a difficulty:
1- Beginner
2- Intermediate
3- Advance
        
        """

        # Welcome messages for the game
        welcome_message1 = """
```
-------------------
  Game Time!!!  
-------------------         
```              
            
            """
        welcome_message2 = """
```
-------------------
   PLATZI TRIVIA  
-------------------         
```       
            """
        # Handle the "$cursos" command to list available courses
        if message.content == "$cursos":
            try:
                await message.author.send(schools)
                response = requests.get(QUESTION_URL)
                json_data = json.loads(response.text)

                try:
                    respuesta = await client.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
                except asyncio.TimeoutError:
                    return await message.author.send(
                        "Ups, you took too long to choose an option 😄"
                        + "\n"
                        + 'Write "$cursos" in the channel, one more time, and try again 😊'
                    )

                school_option = respuesta.content
                await message.author.send(difficulty)
                try:
                    respuesta = await client.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
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
                        respuesta = await client.wait_for(
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
            await message.channel.send(
                f"hello, {message.author.mention}. I sent you a message by DM 😊"
            )
            await message.author.send(
                """We're about to start the Platzi trivia game 🥳.
If it's really time to play, write "go" to choose the theme of the Trivia. If it's not time to play, don't write anything or write anything else 😜"""
            )

            try:
                decision_to_start = await client.wait_for(
                    "message", check=self.start_game, timeout=TIMEOUT_DURATION
                )
            except asyncio.TimeoutError:
                return await message.author.send(
                    "I understand, it's not time to play yet, no problem 😉, we'll play another time 😃"
                )

            if str.lower(decision_to_start.content) == "go":
                await message.author.send(schools)
                await message.channel.send("------Hey!!Trivia time!---------")
                await message.channel.send(welcome_message1)
                await message.channel.send(welcome_message2)
                await message.channel.send("""Soon the game will start, there will be 5 questions and the theme will be one of the Platzi courses, you'll have 30 seconds to read the question and then after the warning, 10 seconds to respond. 
If no one responds, we'll move on to the next question. When someone responds correctly, the next question will appear and they'll earn 10 points.""")
                await message.channel.send("We'll start in 3 ⏳")
                response = requests.get(QUESTION_URL)
                json_data = json.loads(response.text)

            else:
                return await message.author.send(
                    "I understand, it's not time to play yet, no problem 😉, we'll play another time 😃"
                )

            # Collect game parameters (school and difficulty)
            try:
                respuesta = await client.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, you took too long to choose an option 😄"
                    + "\n"
                    + 'Write "$trivia" in the channel, one more time, and try again 😊'
                ), await message.channel.send(
                    "Ups, this is embarrassing 🙈, it seems we had a problem but don't worry, we'll play soon 😄"
                )

            school_option = respuesta.content
            await message.author.send(difficulty)
            await message.channel.send("... 2 ⏳")
            try:
                respuesta = await client.wait_for("message", check=self.options, timeout=TIMEOUT_DURATION)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, you took too long to choose an option 😄"
                    + "\n"
                    + 'Write "$trivia" in the channel one more time, and try again 😊'
                ), await message.channel.send(
                    "Ups, this is embarrassing 🙈, it seems we had a problem but don't worry, we'll play soon 😄"
                )

            difficulty_level = respuesta.content
            # get_course(school_option, difficulty_level)

            course, numero = self.trivia_game.get_course(school_option, difficulty_level)
            while True:
                if numero != 0:
                    await message.author.send("Choose a course:")
                    await message.author.send(course)
                    await message.channel.send("... 1 ⏳")
                    try:
                        respuesta = await client.wait_for(
                            "message", check=self.options, timeout=TIMEOUT_DURATION
                        )
                    except asyncio.TimeoutError:
                        return await message.channel.send("""
Ups, you took too long 😄, if you still don't know about which course to make the game, no problem, review 
the list and then come back with the $trivia command""")

                    if int(respuesta.content) <= numero:
                        position = int(respuesta.content) - 1
                        selected_course = json_data[position]["title"]
                        await message.author.send(
                            "Success in choosing the course. We'll start in 10 seconds 🥳"
                        )
                        break
                    else:
                        await message.author.send(
                            "You chose an incorrect option, please try again 😊"
                        )
                else:
                    await message.author.send(course)
                    await message.author.send(
                        "you can go to the game admin to add it and come back to play again 😃"
                    )
                    break

            # Game action: ask questions and handle answers
            question_counter = 0
            while question_counter <= MAX_QUESTIONS - 1:
                await game()
                question_counter += 1
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

    @staticmethod
    def check(message):
        return message.content.isdigit()

    @staticmethod
    def options(message):
        return message.content.isdigit()

    @staticmethod
    def start_game(message):
        return message.content

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# Run the Discord bot
client.run(DISCORD_KEY)
# Commented out alternative bot token (for testing purposes)
# client.run("MTI3MTY2NjkyNzgyMzA5Mzg1NA.GajfAW.IzdlKYgp_AWl9Vgsz7ExGGohelJ3bTKAEJKPr8")