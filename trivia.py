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


def get_question():
        question = ''
        id = 1
        answer = 0
        points = 0 
        #response = requests.get('https://djangodiscordtriviabot.herokuapp.com/api/question/')
        response = requests.get('http://127.0.0.1:8000/api/question')
        json_data = json.loads(response.text)
        question += 'Pregunta: \n\n'
        question += json_data[0]['title'] + '\n\n'

        for item in json_data[0]['answer']:
            question += str(id) + '-' + item['answer'] + '\n\n'

            if item['is_correct']:
                answer = id
            id += 1

        points = json_data[0]['points']
        return(question, answer, points)


class MyClient(discord.Client):

    async def on_ready(self):
        print('nos conectamos como', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == '$puntaje':
            leaderboard = get_score()
            await message.channel.send(leaderboard)

        if message.content =='$trivia':
            
            question, answer, points = get_question()
            await message.channel.send(question)
        
            def check(message):
                return message.author ==message.author and message.content.isdigit()

            try:
                guess = await client.wait_for('message',check=check, timeout= 10.0)
            except asyncio.TimeoutError:
                return await message.channel.send('Ops, te demoraste mucho 🥲')

            if int(guess.content) == answer:
                user = guess.author
                mensaje = '¡Correcto! ' + str(guess.author.name) + ', ganaste ' + str(points) + ' puntos 🥳'
                await message.channel.send(mensaje)
                update_score(user, points)
            else:
                await message.channel.send('Uy no, esa no es la respuesta 😞')




intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('MTAwOTEyMjE2MTU2ODUzNDY1OQ.G5hOpM._iDXKZvyRHEu_IhQGOzUTnx6VA7LtLryc773sc')
