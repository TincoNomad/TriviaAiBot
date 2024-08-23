import discord
from config import DISCORD_KEY
from .discord_client import MyClient

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

# Run the Discord bot
client.run(DISCORD_KEY) #type: ignore