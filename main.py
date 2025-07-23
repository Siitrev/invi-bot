import os, environ, discord
from discord.ext import commands

class PhantomBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents, application_id=APP_ID)

        self.initial_extentions = ["cogs.rolls",
                                    "cogs.interactions"]

    async def setup_hook(self):
        for cog in self.initial_extentions:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        if not os.path.exists("data"):
            os.mkdir("data")
        
        if not os.path.exists("data/urls.json"):
            with open("data/urls.json", "w") as file:
                file.write(r"{}")

        print(f"We've logged in as {self.user}")

    async def close(self):
        await super().close()

env = environ.Env()
env.read_env(".env")

TOKEN = os.environ.get("DISCORD_TOKEN")
APP_ID = os.environ.get("APP_ID")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = PhantomBot(intents=intents)

bot.run(TOKEN)