import discord
import requests
import json

def get_question():
        qs = ''
        id = 1
        answer = 0  
        response = requests.get('')
        json_data = json.loads(response.text)
        qs += 'Question: \n'
        qs += json_data[0]['title'] + '\n'

        for item in json_data[0]['answer']:
            qs += str(id) + '.' + item['answer'] + '\n'

            if item['is_correct']:
                answer = id

                id += 1

        return(qs, answer)


class MyClient(discord.Client):

    async def on_ready(self):
        print('nos conectamos como', self.user)

    async def on_message(self, message):
        if message.author == self.user:
            return


        if message.content =='$trivia':
            print('message')
            qs, answer = get_question()
            await message.channel.send('hi I am the bot')



intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

client.run('MTAwOTEyMjE2MTU2ODUzNDY1OQ.G5hOpM._iDXKZvyRHEu_IhQGOzUTnx6VA7LtLryc773sc')