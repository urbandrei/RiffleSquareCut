"""Discord bot client with cog loading."""

import discord
from discord.ext import commands


class SalesBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        cog_modules = [
            "bot.cogs.help_cmd",
            "bot.cogs.customers",
            "bot.cogs.sales",
            "bot.cogs.invoices",
            "bot.cogs.queries",
            "bot.cogs.reports",
            "bot.cogs.inventory",
            "bot.cogs.contacts",
            "bot.cogs.notebook",
            "bot.cogs.livechat",
        ]
        for module in cog_modules:
            await self.load_extension(module)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Connected to {len(self.guilds)} guild(s)")
        print("------")
