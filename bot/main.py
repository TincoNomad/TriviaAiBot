import discord
from env import env
from .discord_client import MyClient

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# Run the Discord bot
client.run(env('DISCORD_KEY')) #type: ignore