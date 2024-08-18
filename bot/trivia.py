import asyncio
import discord
import requests
import json
from config import LEADERBOARD_URL, SCORE_URL, QUESTION_URL, DISCORD_KEY


# Fetch and format the leaderboard data
def get_score():
    leaderboard = ""
    id = 1
    response = requests.get(LEADERBOARD_URL)
    try:
        json_data = json.loads(response.text)
        if not isinstance(json_data, list):
            raise ValueError("The response is not a list of dictionaries")
    except (json.JSONDecodeError, ValueError) as e:
        return f"Error getting scores: {e}"

    for item in json_data:
        if not isinstance(item, dict):
            return "Error: An element in the list is not a dictionary"
        leaderboard += (
            str(id)
            + " - "
            + item["name"]
            + "- "
            + str(item["points"])
            + " Points"
            + "\n"
        )
        id += 1

    if leaderboard == "":
        return "No score yet, no games have been played"
    else:
        return leaderboard

# Update player's score in the database
def update_score(name, points):
    url = SCORE_URL
    new_score = {"name": name, "points": points}
    response = requests.post(url, data=new_score)
    return response.status_code


# Fetch available courses based on school and difficulty level
def get_course(school_option, difficulty_level):
    course = ""
    numero = 1
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)

    for item in json_data:
        if item["school"] == int(school_option) and item["difficulty"] == int(
            difficulty_level
        ):
            course += "\n" + str(numero) + "-" + item["title"]
            numero += 1

    if course == "":
        course = "Oops, this is embarrassing, but it seems we don't have courses with those categories yet 😅"
        numero = 0

    return (course, numero)


# Fetch a specific question for the selected course
def get_question(selected_course, question_counter):
    question = ""
    id = 1
    answer = ""
    points = 0
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)
    questionOptions = [i["question"] for i in json_data if i["title"] == selected_course]

    question += questionOptions[0][question_counter]["questionTitle"] + "\n\n"
    for item in questionOptions[0][question_counter]["answer"]:
        question += str(id) + "-" + item["answerTitle"] + "\n"

        if item["is_correct"]:
            answer = id
        id += 1
    points = questionOptions[0][0]["points"]

    return question, answer, points


# Get the URL for the selected course
def getLink(selected_course):
    url = ""
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)
    for i in json_data:
        if i["title"] == selected_course:
            url = i["url"]
    return url

# Check if the message is a valid numeric response
def check(message):
    return message.author == message.author and message.content.isdigit()

# Main Discord Bot class
class MyClient(discord.Client):
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

            question, answer, points = get_question(selected_course, question_counter)
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
                    guess = await client.wait_for("message", check=check, timeout=30)
                except asyncio.TimeoutError:
                    return await message.channel.send(
                        "ohhh, it seems no one guessed this 😔. Well, let's move on to the next one 💪🏽"
                    )

                player_info = str(guess.author.name) + str(guess.author.discriminator)

                if player_info not in players:
                    if int(guess.content) == answer:
                        user = guess.author
                        mensaje = (
                            "Correct! "
                            + str(guess.author.name)
                            + ", you won "
                            + str(points)
                            + " points 🥳"
                            + "\n\n"
                        )
                        await message.channel.send(mensaje)
                        update_score(user, points)
                        players.append(player_info)
                        break

                    else:
                        await message.channel.send(
                            "Uh no "
                            + (guess.author.name)
                            + ", that's not the answer 😞"
                            + "\n\n"
                        )
                        user = guess.author
                        points = 0
                        players.append(player_info)
                        update_score(user, points)
                else:
                    await message.channel.send(
                        (guess.author.name) + ", You can only try once 🙈"
                    )

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
            await message.author.send(schools)
            response = requests.get(QUESTION_URL)
            json_data = json.loads(response.text)

            def options(message):
                return message.content.isdigit()

            try:
                respuesta = await client.wait_for("message", check=options, timeout=40)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, you took too long to choose an option 😄"
                    + "\n"
                    + 'Write "$cursos" in the channel, one more time, and try again 😊'
                )

            school_option = respuesta.content
            await message.author.send(difficulty)
            try:
                respuesta = await client.wait_for("message", check=options, timeout=40)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, you took too long to choose an option 😄"
                    + "\n"
                    + 'Write "$cursos" in the channel one more time, and try again 😊'
                )

            difficulty_level = respuesta.content
            get_course(school_option, difficulty_level)

            course, numero = get_course(school_option, difficulty_level)

            if numero != 0:
                await message.author.send(course)
                await message.author.send(
                    "`If you don't see the course you're looking for, you can ask for it to be added to the game 😊`"
                )
                try:
                    respuesta = await client.wait_for(
                        "message", check=options, timeout=60
                    )
                except asyncio.TimeoutError:
                    return await message.author.send(
                        '`If you need more time, you can write "$cursos" in the channel again 😊`'
                    )

        # Handle the "$trivia" command to start the game
        if message.content == "$trivia":
            await message.channel.send(
                "hello, " + message.author.mention + ". I sent you a message by DM 😊"
            )
            await message.author.send(
                """We're about to start the Platzi trivia game 🥳.
If it's really time to play, write "go" to choose the theme of the Trivia. If it's not time to play, don't write anything or write anything else 😜"""
            )

            def start_game(message):
                return message.content

            try:
                decision_to_start = await client.wait_for(
                    "message", check=start_game, timeout=40
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
            def options(message):
                return message.content.isdigit()

            try:
                respuesta = await client.wait_for("message", check=options, timeout=30)
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
                respuesta = await client.wait_for("message", check=options, timeout=30)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, you took too long to choose an option 😄"
                    + "\n"
                    + 'Write "$trivia" in the channel one more time, and try again 😊'
                ), await message.channel.send(
                    "Ups, this is embarrassing 🙈, it seems we had a problem but don't worry, we'll play soon 😄"
                )

            difficulty_level = respuesta.content
            get_course(school_option, difficulty_level)

            course, numero = get_course(school_option, difficulty_level)
            while True:
                if numero != 0:
                    await message.author.send("Choose a course:")
                    await message.author.send(course)
                    await message.channel.send("... 1 ⏳")
                    try:
                        respuesta = await client.wait_for(
                            "message", check=options, timeout=30
                        )
                    except asyncio.TimeoutError:
                        return await message.channel.send("""
Ups, you took too long 😄, if you still don't know about which course to make the game, no problem, review 
the list and then come back with the $trivia command""")

                    if int(respuesta.content) < numero:
                        position = int(respuesta.content) - 1
                        selected_course = json_data[position]["title"]
                        await message.author.send(
                            "Success in choosing the course. We'll start in 10 seconds 🥳"
                        )

                    elif int(respuesta.content) >= numero:
                        await message.author.send(
                            "You chose an incorrect option, please try again 😊"
                        )
                        continue
                    question_counter = 0
                    get_question(selected_course, question_counter)
                    getLink(selected_course)
                else:
                    await message.author.send(course)
                    await message.author.send(
                        "you can go to the game admin to add it and come back to play again 😃"
                    )
                    break

                # Game action: ask questions and handle answers
                while question_counter <= 4:
                    await game()
                    question_counter += 1
                await message.channel.send("""
```
   End of the Game. Thanks for participating 💚          
``` 
                """)
                await message.channel.send(
                    "It was very fun 💃🕺 Congratulations!" + "\n" + "Final Score: "
                )
                await score()
                url = getLink(selected_course)
                await message.channel.send("The theme of this game was the course " + url)
                break

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# Run the Discord bot
client.run(DISCORD_KEY)
# Commented out alternative bot token (for testing purposes)
# client.run("MTI3MTY2NjkyNzgyMzA5Mzg1NA.GajfAW.IzdlKYgp_AWl9Vgsz7ExGGohelJ3bTKAEJKPr8")