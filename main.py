import os, discord, lavalink
from discord.ext import commands
from common.settings import TOKEN, APP_ID

class PhantomBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents, application_id=APP_ID)

        self.lavalink: None | lavalink.Client = None
        self.initial_extentions = ["cogs.rolls",
                                    "cogs.interactions",
                                    "cogs.music_player"]

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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = PhantomBot(intents=intents)

bot.run(TOKEN)