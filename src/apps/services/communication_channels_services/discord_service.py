import os

import discord
from dotenv import load_dotenv

from apps.bot.services.bot_service import BotService


class DiscordService:
    def __init__(self):
        load_dotenv()
        self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
        self.bot_service = BotService()

        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True

        self.client = discord.Client(intents=intents)
        self.client.event(self.on_ready)
        self.client.event(self.on_message)

    async def on_ready(self):
        print(f"Logged in as {self.client.user}!")

    async def on_message(self, message):
        if message.author == self.client.user:
            return

        print("Mensaje recibido por canal de comunicación:", message.content)
        response = await self.bot_service.handle_message(message.content)
        await message.channel.send(response)

    def run(self):
        self.client.run(self.DISCORD_TOKEN)
