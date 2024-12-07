import discord
from env import env
from bot.discord_client import DiscordClient

# Set up Discord bot connection
intents = discord.Intents.default()
intents.message_content = True
client = DiscordClient()

# Run the Discord bot
client.run(env('DISCORD_KEY')) #type: ignore