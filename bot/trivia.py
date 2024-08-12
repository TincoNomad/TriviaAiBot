import asyncio
import discord
import requests
import json
from config import LEADERBOARD_URL, SCORE_URL, QUESTION_URL, DISCORD_KEY


###### Game data base get points ######
def get_score():
    leaderboard = ""
    id = 1
    response = requests.get(LEADERBOARD_URL)
    try:
        json_data = json.loads(response.text)
        if not isinstance(json_data, list):
            raise ValueError("La respuesta no es una lista de diccionarios")
    except (json.JSONDecodeError, ValueError) as e:
        return f"Error al obtener los puntajes: {e}"

    for item in json_data:
        if not isinstance(item, dict):
            return "Error: Un elemento en la lista no es un diccionario"
        leaderboard += (
            str(id)
            + " - "
            + item["name"]
            + "- "
            + str(item["points"])
            + " Puntos"
            + "\n"
        )
        id += 1

    if leaderboard == "":
        return "Aun no hay puntaje, no se ha jugado ninguna partida"
    else:
        return leaderboard

###### Game data base save points ######
def update_score(name, points):
    url = SCORE_URL
    new_score = {"name": name, "points": points}
    response = requests.post(url, data=new_score)
    return response.status_code


###### Game data base Courses ######
def get_course(opcionEscuela, opcionNivel):
    course = ""
    numero = 1
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)

    for item in json_data:
        if item["school"] == int(opcionEscuela) and item["difficulty"] == int(
            opcionNivel
        ):
            course += "\n" + str(numero) + "-" + item["title"]
            numero += 1

    if course == "":
        course = "Ups, esto es vergonzoso, pero parece que aun no tenemos cursos con esas categorias 😅"
        numero = 0

    return (course, numero)


###### Game data base Questions ######
def get_question(opcionCurso, counter):
    question = ""
    id = 1
    answer = ""
    points = 0
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)
    questionOptions = [i["question"] for i in json_data if i["title"] == opcionCurso]

    question += questionOptions[0][counter]["questionTitle"] + "\n\n"
    for item in questionOptions[0][counter]["answer"]:
        question += str(id) + "-" + item["answerTitle"] + "\n"

        if item["is_correct"]:
            answer = id
        id += 1
    points = questionOptions[0][0]["points"]

    return question, answer, points


# get course url
def getLink(opcionCurso):
    url = ""
    response = requests.get(QUESTION_URL)
    json_data = json.loads(response.text)
    for i in json_data:
        if i["title"] == opcionCurso:
            url = i["url"]
    return url

def check(message):
    return message.author == message.author and message.content.isdigit()

############Discord Bot#########
class MyClient(discord.Client):
    # confirm bot conection
    async def on_ready(self):
        print("nos conectamos como", self.user)

    # sotp bot for looping
    async def on_message(self, message):
        if message.author == self.user:
            return

        # save game's palyers score
        async def score():
            leaderboard = get_score()
            await message.channel.send(leaderboard)

        # get game's palyers score
        if message.content == "$puntaje":
            await score()

        # game logic
        async def juego():
            await asyncio.sleep(10)
            await message.channel.send("""
```
------------ PREGUNTA -------------        
``` 
            """)

            question, answer, points = get_question(opcionCurso, counter)
            # question, answer = get_question(opcionCurso,counter)

            await message.channel.send(
                "----------------------------------"
                + "\n"
                + "Lee la pregunta, tienes 30 segundos"
            )
            await message.channel.send(question)
            # await message.channel.send('----------------------------------'+'\n'+'🕰️ Espera, que te voy a avisar cuando responder 🕰️')

            # def check(message):
            #     return message.author == message.author and message.content.isdigit()

            await attempt(answer, points)

        async def attempt(answer, points):
            players = []

            while True:
                try:
                    guess = await client.wait_for("message", check=check, timeout=30)
                except asyncio.TimeoutError:
                    return await message.channel.send(
                        "ohhh, parece que nadie adivino esta 😔. Bueno vamos a la siguiente 💪🏽"
                    )

                player_info = str(guess.author.name) + str(guess.author.discriminator)

                if player_info not in players:
                    if int(guess.content) == answer:
                        user = guess.author
                        mensaje = (
                            "¡Correcto! "
                            + str(guess.author.name)
                            + ", ganaste "
                            + str(points)
                            + " puntos 🥳"
                            + "\n\n"
                        )
                        await message.channel.send(mensaje)
                        update_score(user, points)
                        players.append(player_info)
                        break

                    else:
                        await message.channel.send(
                            "Uy no "
                            + (guess.author.name)
                            + ", esa no es la respuesta 😞"
                            + "\n\n"
                        )
                        user = guess.author
                        points = 0
                        players.append(player_info)
                        update_score(user, points)
                else:
                    await message.channel.send(
                        (guess.author.name) + ", Solo puedes intentar una vez 🙈"
                    )

        ###### Begining of the game #######
        # school options
        escuelas = """
Escoje una escuela:
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

        # difficulty options
        dificultad = """
Escoje una dificulatad:
1- Beginner
2- Intermediate
3- Advance
        
        """

        # Welcome messages
        mensaje1 = """
```
-------------------
  ¡¡¡Game Time!!!  
-------------------         
```              
            
            """
        mensaje2 = """
```
-------------------
   TRIVIA PLATZI  
-------------------         
```       
            """
        # begining of interaction
        if message.content == "$cursos":
            await message.author.send(escuelas)
            response = requests.get(QUESTION_URL)
            json_data = json.loads(response.text)

            def opciones(message):
                return message.content.isdigit()

            try:
                respuesta = await client.wait_for("message", check=opciones, timeout=40)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, te demoraste mucho en escoger una opción 😄"
                    + "\n"
                    + 'Escribe "$cursos" en el canal,una vez más, e intentalo nuevamente 😊'
                )

            opcionEscuela = respuesta.content
            await message.author.send(dificultad)
            try:
                respuesta = await client.wait_for("message", check=opciones, timeout=40)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, te demoraste mucho en escoger una opción 😄"
                    + "\n"
                    + 'Escribe "$cursos" en el canal una vez más, e intentalo nuevamente 😊'
                )

            opcionNivel = respuesta.content
            get_course(opcionEscuela, opcionNivel)

            course, numero = get_course(opcionEscuela, opcionNivel)

            if numero != 0:
                await message.author.send(course)
                await message.author.send(
                    "`Si no ves el curso que buscas puedes pedir que lo agreguen al juego  😊`"
                )
                try:
                    respuesta = await client.wait_for(
                        "message", check=opciones, timeout=60
                    )
                except asyncio.TimeoutError:
                    return await message.author.send(
                        '`Si necesitas más tiempo puedes escribir "$cursos", en el canal otra vez 😊`'
                    )

        ###### Begining of the game #######
        if message.content == "$trivia":
            await message.channel.send(
                "hola, " + message.author.mention + ". Te envie un mensaje por DM 😊"
            )
            await message.author.send(
                """Estamos a punto de comenzar el juego de trivias con Platzi 🥳.
Si en verdad es tiempo de jugar escrive "go" para escojer el tema de la Trivie. Si no es momento de jugar, no escribas nada o escribe cualqueir otra cosa 😜"""
            )

            def comenzar(message):
                return message.content

            try:
                desicion_comenzar = await client.wait_for(
                    "message", check=comenzar, timeout=40
                )
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Entiendo, aun no es tiempo de jugar , no hay problema 😉, jugaremos en otro momento 😃"
                )

            if str.lower(desicion_comenzar.content) == "go":
                await message.author.send(escuelas)
                await message.channel.send("------¡Hey!!Trivia time!---------")
                await message.channel.send(mensaje1)
                await message.channel.send(mensaje2)
                await message.channel.send("""Dentro de poco comenzará el juego, seran 5 preguntas y el tema sera uno de lo cursos 
de Platzi, tendrán 30 segundos para leer la pregunta y luego del aviso, 10 seg para responder. 
Si nadie responder se pasara a la siguiente pregunta. Cuando alguien responda correctamente aparecera la siguietne pregunta y ganara 10 puntos.""")
                await message.channel.send("Comenzamos en 3 ⏳")
                response = requests.get(QUESTION_URL)
                json_data = json.loads(response.text)

            else:
                return await message.author.send(
                    "Entiendo, aun no es tiempo de jugar , no hay problema 😉, jugaremos en otro momento 😃"
                )

            # recolect parameters
            def opciones(message):
                return message.content.isdigit()

            try:
                respuesta = await client.wait_for("message", check=opciones, timeout=30)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, te demoraste mucho en escoger una opción 😄"
                    + "\n"
                    + 'Escribe "$trivia" en el canal,una vez más, e intentalo nuevamente 😊'
                ), await message.channel.send(
                    "Ups, esto es vergonzoso 🙈, parece que tuvimos un problema pero no te preocupes, jugaremos pronto 😄"
                )

            opcionEscuela = respuesta.content
            await message.author.send(dificultad)
            await message.channel.send("... 2 ⏳")
            try:
                respuesta = await client.wait_for("message", check=opciones, timeout=30)
            except asyncio.TimeoutError:
                return await message.author.send(
                    "Ups, te demoraste mucho en escoger una opción 😄"
                    + "\n"
                    + 'Escribe "$trivia" en el canal una vez más, e intentalo nuevamente 😊'
                ), await message.channel.send(
                    "Ups, esto es vergonzoso 🙈, parece que tuvimos un problema pero no te preocupes, jugaremos pronto 😄"
                )

            opcionNivel = respuesta.content
            get_course(opcionEscuela, opcionNivel)

            course, numero = get_course(opcionEscuela, opcionNivel)
            while True:
                if numero != 0:
                    await message.author.send("Escoje un curso:")
                    await message.author.send(course)
                    await message.channel.send("... 1 ⏳")
                    try:
                        respuesta = await client.wait_for(
                            "message", check=opciones, timeout=30
                        )
                    except asyncio.TimeoutError:
                        return await message.channel.send("""
Ups, te demoraste mucho 😄, si aun no sabes sobre cual curso hacer el juego no hay problema, revisa 
la lista y luego vuelve a colocar el comando $trivia""")

                    if int(respuesta.content) < numero:
                        position = int(respuesta.content) - 1
                        opcionCurso = json_data[position]["title"]
                        await message.author.send(
                            "Exito al esoger el curso. Empezamos en 10 segundo 🥳"
                        )

                    elif int(respuesta.content) >= numero:
                        await message.author.send(
                            "Has escogido un opción incorrecta, por favor intenta de nuevo 😊"
                        )
                        continue
                    counter = 0
                    get_question(opcionCurso, counter)
                    getLink(opcionCurso)
                else:
                    await message.author.send(course)
                    await message.author.send(
                        "puedes ingresar a el admin del juego para agregarlo y volver para jugar nuevamente 😃"
                    )
                    break

                # game action.
                while counter <= 4:
                    await juego()
                    counter += 1
                await message.channel.send("""
```
   Fin del Juego. Gracias por participar 💚          
``` 
                """)
                await message.channel.send(
                    "Fue muy divertido 💃🕺 ¡Felicidades!" + "\n" + "Puntaje final: "
                )
                await score()
                url = getLink(opcionCurso)
                await message.channel.send("El tema de este juego fue el curso " + url)
                break


##### Discord bot conection ######
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run(DISCORD_KEY)
# client.run("MTI3MTY2NjkyNzgyMzA5Mzg1NA.GajfAW.IzdlKYgp_AWl9Vgsz7ExGGohelJ3bTKAEJKPr8")