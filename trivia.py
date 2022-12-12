import asyncio
import discord
import requests
import json


def get_score():
    leaderboard = ''
    id = 1
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/score/leaderboard')
    response = requests.get('http://127.0.0.1:8000/api/score/leaderboard')
    json_data = json.loads(response.text)

    for item in json_data:
        leaderboard += str(id)+' - '+ item['name'] + ', '+str(item['points']) + 'Puntos' + '\n'

        id += 1

    return(leaderboard)

def update_score(name, points):
    #url = 'https://djangodiscordtriviabot.herokuapp.com/api/score'
    url = 'http://127.0.0.1:8000/api/score'
    new_score = {'name': name, 'points': points}
    x = requests.post(url, data=new_score)

def get_course(opcionEscuela, opcionNivel):
    course = ''
    numero = 1
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
    response = requests.get('http://127.0.0.1:8000/api/question')
    json_data = json.loads(response.text)
    for item in json_data:
        if item['school'] == int(opcionEscuela) and item['difficulty'] == int(opcionNivel):
            course += '\n' + str(numero) + '-' + item['title']
        
        item['title'] = numero
        numero += 1

    return(course,numero)

def get_question(opcionCurso):

    question = ''
    id = 1
    answer = ''
    points = 0
    url = ''
    #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
    response = requests.get('http://127.0.0.1:8000/api/question')
    json_data = json.loads(response.text)
    questionOptions = [i['question'] for i in json_data if i['title'] == opcionCurso]

    for i in json_data:
        if i['title'] == opcionCurso:
            url = i['url']

    question += questionOptions[0][0]['questionTitle'] + '\n\n'
    for item in questionOptions[0][0]['answer']:
            question += str(id) + '-' + item['answerTitle'] + '\n'

            if item['is_correct']:
                answer = id
            id += 1
    points = questionOptions[0][0]['points']
    
    return question, answer, points, url,


class MyClient(discord.Client):

    async def on_ready(self):
        print('nos conectamos como', self.user)

    async def on_message(self, message):

        if message.author == self.user:
            return

        async def puntaje():
            if message.content == '$puntaje':
                leaderboard = get_score()
                await message.channel.send(leaderboard)

        async def juego():
                    
            question, answer, points, url = get_question(opcionCurso)
            await message.channel.send(question)
                
            def check(message):
                return message.author ==message.author and message.content.isdigit()

            try:
                guess = await client.wait_for('message',check=check, timeout= 5.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Ops, te demoraste mucho 🥲' + ', estas preguntas son del curso ' + url)

            if int(guess.content) == answer:
                user = guess.author
                mensaje = '¡Correcto! ' + str(guess.author.name) + ', ganaste ' + str(points) + ' puntos 🥳'
                await message.channel.send(mensaje)
                update_score(user, points)
                #await message.channel.send(leaderboard)
                await message.channel.send('estas preguntas son del curso ' + url)

            else:
                await message.channel.send('Uy no, esa no es la respuesta 😞')

        if message.content == "$trivia":

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
            dificultad = '''
Escoje una dificulatad:
1- Beginner
2- Intermediate
3- Advance
        
        '''
        
            await message.channel.send('super!!! Comencemos!!!')
            await message.channel.send(escuelas)

            def opciones(message):
                #return message.author ==message.author and message.content.isdigit()
                return message.content.isdigit()
            try:
                respuesta = await client.wait_for('message',check=opciones)
            except asyncio:
                return await message.channel.send('Ops, te demoraste mucho 🥲')
            opcionEscuela = respuesta.content
            await message.channel.send(dificultad)
            try:
                respuesta = await client.wait_for('message',check=opciones)
            except asyncio:
                return await message.channel.send('Ops, te demoraste mucho 🥲')
            opcionNivel = respuesta.content
            get_course(opcionEscuela, opcionNivel)
            curso, numero = get_course(opcionEscuela, opcionNivel)
            await message.channel.send('Escoje un curso:')
            await message.channel.send(curso)
            try:
                respuesta = await client.wait_for('message',check=opciones)
            except asyncio:
                return await message.channel.send('Ops, te demoraste mucho 🥲')
            if respuesta.content == numero:
                return curso
            opcionCurso = curso[3:]
            get_question(opcionCurso)
            await juego()
            




intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('MTAwOTEyMjE2MTU2ODUzNDY1OQ.G5hOpM._iDXKZvyRHEu_IhQGOzUTnx6VA7LtLryc773sc')
