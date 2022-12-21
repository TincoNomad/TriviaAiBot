import asyncio
import discord
import requests
import json


###### Game data base get points ######
def get_score():
    leaderboard = ''
    id = 1
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/score/leaderboard')
    response = requests.get('http://127.0.0.1:8000/api/score/leaderboard')
    json_data = json.loads(response.text)

    for item in json_data:
        leaderboard += str(id)+' - '+ item['name'] + '- '+str(item['points']) + 'Puntos' + '\n'

        id += 1

    return(leaderboard)

###### Game data base save points ######
def update_score(name, points):
    #url = 'https://djangodiscordtriviabot.herokuapp.com/api/score'
    url = 'http://127.0.0.1:8000/api/score'
    new_score = {'name': name, 'points': points}
    x = requests.post(url, data=new_score)

###### Game data base Courses ######
def get_course(opcionEscuela, opcionNivel):
    course = ''
    numero = 1
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
    response = requests.get('http://127.0.0.1:8000/api/question')
    json_data = json.loads(response.text)
    for item in json_data:
        if item['school'] == int(opcionEscuela) and item['difficulty'] == int(opcionNivel):
            course += '\n' + str(numero) + '-' + item['title']
            numero += 1
        else:
            course = 'Ups, esto es vergonzoso, pero parece que aun no tenemos cursos con esas categorias 😅'
    
    if course == 'Ups, esto es vergonzoso, pero parece que aun no tenemos cursos con esas categorias 😅':
        numero = 0

    return(course,numero)

###### Game data base Questions ######
def get_question(opcionCurso,counter):

    question = ''
    id = 1
    answer = ''
    points = 0
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
    response = requests.get('http://127.0.0.1:8000/api/question')
    json_data = json.loads(response.text)
    questionOptions = [i['question'] for i in json_data if i['title'] == opcionCurso]
        
    question += questionOptions[0][counter]['questionTitle'] + '\n\n'
    for item in questionOptions[0][counter]['answer']:
            question += str(id) + '-' + item['answerTitle'] + '\n'

            if item['is_correct']:
                answer = id
            id += 1
    points = questionOptions[0][0]['points']

    return question, answer, points


#get course url
def getLink(opcionCurso):
    url = ''
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
    response = requests.get('http://127.0.0.1:8000/api/question')
    json_data = json.loads(response.text)
    for i in json_data:
        if i['title'] == opcionCurso:
            url = i['url']
    return url


############Discord Bot#########
class MyClient(discord.Client):

#confirm bot conection
    async def on_ready(self):
        print('nos conectamos como', self.user)

#sotp bot for looping
    async def on_message(self, message):

        if message.author == self.user:
            return

#save game's palyers score 
        async def score():
            leaderboard = get_score()
            await message.channel.send(leaderboard)

#get game's palyers score         
        if message.content == '$puntaje':
            await score()

#game logic
        async def juego():
            
            question, answer, points = get_question(opcionCurso,counter)

            await message.channel.send(question)
                
            def check(message):
                return message.author ==message.author and message.content.isdigit()

            try:
                guess = await client.wait_for('message',check=check, timeout= 10.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Ops, te demoraste mucho 🥲')
            await asyncio.sleep(10.0)

            if int(guess.content) == answer:
                user = guess.author
                mensaje = '¡Correcto! ' + str(guess.author.name) + ', ganaste ' + str(points) + ' puntos 🥳' + '\n\n'
                await message.channel.send(mensaje)
                update_score(user, points)
            else:
                await message.channel.send('Uy no '+ str(guess.author.name) +', esa no es la respuesta 😞' + '\n\n')

###### Begining of the game #######         
        if message.content == "$trivia":

            response = requests.get('http://127.0.0.1:8000/api/question')
            json_data = json.loads(response.text)

#school options
            escuelas = '''
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
        
        '''

#difficulty options
            dificultad = '''
Escoje una dificulatad:
1- Beginner
2- Intermediate
3- Advance
        
        '''

#Welcome messages
            mensaje1 = '''
```yaml
-------------------
  ¡¡¡Game Time!!!  
-------------------         
```              
            
            '''
            mensaje2 = '''
```yaml
-------------------
   TRIVIA PLATZI  
-------------------         
```       
            '''
#begining of interaction
            

            await message.channel.send(mensaje1)
            await message.channel.send(mensaje2)
            await message.channel.send('''Dentro de poco comenzará el juego, seran 5 preguntas y el tema sera uno de lo cursos 
de Platzi, tendrán 10 segundos para escoger una respuesta''')

            await message.channel.send('Comenzamos en 3 ⏳')
            await message.author.send(escuelas)

#recolect parameters
            def opciones(message):

                return message.content.isdigit()
            try:
                respuesta = await client.wait_for('message',check=opciones, timeout= 15.0)
            except asyncio.TimeoutError:
                return await message.author.send('Ups, te demoraste mucho en escoger una opción 😄'), await message.channel.send('''Ups, esto es vergonzoso pero parece que tuvimos un problema, no
te preocupes, tendremos otro momento para jugar. No pares de aprender 🚀''')

            opcionEscuela = respuesta.content
            await message.channel.send('... 2 ⏳')
            await message.author.send(dificultad)
            try:
                respuesta = await client.wait_for('message',check=opciones, timeout= 15.0)
            except asyncio.TimeoutError:
                return await message.author.send('Ups, te demoraste mucho en escoger una opción 😄'), await message.channel.send('''Ups, esto es vergonzoso pero parece que tuvimos un problema, no
te preocupes, tendremos otro momento para jugar. No pares de aprender 🚀''')

            opcionNivel = respuesta.content
            get_course(opcionEscuela, opcionNivel)

#Choosing a course for the game
            course, numero = get_course(opcionEscuela, opcionNivel)
            await message.channel.send('... 1 ⏳')
            while True:
                if numero != 0:
                    await message.author.send('Escoje un curso:')
                    await message.author.send(course)
                    try:
                        respuesta = await client.wait_for('message',check=opciones, timeout= 15.0)
                    except asyncio.TimeoutError:
                        return await message.author.send('''
Ups, te demoraste mucho 😄, si aun no sabes sobre cual curso hacer el juego no hay problema, revisa 
la lista y luego vuelve a colocar el comando $trivia'''), await message.channel.send('''Ups, esto es vergonzoso pero parece que tuvimos un problema, no
te preocupes, tendremos otro momento para jugar. No pares de aprender 🚀''')

                    if int(respuesta.content) < numero:
                        position = int(respuesta.content) - 1
                        opcionCurso = json_data[position]['title']

                    elif int(respuesta.content) >= numero:
                        await message.author.send('Has escogido un opción incorrecta, por favor intenta de nuevo 😊')
                        continue
                    #opcionCurso = cursoElegido[3:]
                    counter = 0
                    get_question(opcionCurso,counter)
                    getLink(opcionCurso)
                    #continue
                else:
                        #await message.channel.send(curso)
                    await message.channel.send('''Ups, esto es vergonzoso pero parece que tuvimos un problema, no
te preocupes, tendremos otro momento para jugar. No pares de aprender 🚀''')

                    await message.author.send(course)
                    await message.author.send('puedes ingresar a el admin del juego para agregarlo y volver para jugar nuevamente 😃')
                    break

# game action.
                counter = 0
                while counter <= 4:
                    await juego()
                    counter += 1
                await message.channel.send('''
```yaml
   Fin del Juego. Gracias por participar 💚          
``` 
                ''')
                await message.channel.send('Fue muy divertido 💃🕺 ¡Felicidades!' + '\n' + 'Puntaje final: ')
                await score()
                url = getLink(opcionCurso)
                await message.channel.send('El tema de este juego fue el curso ' + url)
                break

##### Discord bot conection ######            
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('MTAwOTEyMjE2MTU2ODUzNDY1OQ.G5hOpM._iDXKZvyRHEu_IhQGOzUTnx6VA7LtLryc773sc')