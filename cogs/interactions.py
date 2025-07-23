import discord, json
from discord.ext import commands
from discord import app_commands

DEFAULT_GIF_URL = "https://cdn.discordapp.com/attachments/720181859182706711/1397638120760934420/hop-on-roll20.gif?ex=6882736e&is=688121ee&hm=b3c53a847ebccda7b3dc5ef9ac06357710314780b902ac792193b705f37d5282&"
DEFAULT_URL = "https://app.roll20.net/join/18778491/A34BBw"

class Interactions(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="hop", description="Wskocz na zakrec20")
    @app_commands.describe(url="Zmien link wysylany przez bota. Link musi byc pelny!", gif_url="Zmien gifa wyslanego przez bota. Link do gifa musi byc pelny!")
    async def roll20(self, interaction: discord.Interaction, url: str = None, gif_url: str = None) -> None:
        guild_id = str(interaction.guild_id)   
        
        with open("data/urls.json") as file:
            urls: dict[str, dict] = json.load(file)
            urls.setdefault(guild_id, dict())
            
        if url or gif_url:
            if url:
                urls[guild_id]["url"] = url
            if gif_url:
                urls[guild_id]["gif_url"] = gif_url
                
            with open("data/urls.json", "w") as file:
                json.dump(urls, file)
            
            await interaction.response.send_message(content="Zmieniono linki :horse:", ephemeral=True)
            return
                
        await interaction.response.send_message(content="Przypomnienie wyslane :horse:", ephemeral=True)
        
        await interaction.channel.send(content=urls[guild_id].get("gif_url", DEFAULT_GIF_URL))
        await interaction.channel.send(content=urls[guild_id].get("url", DEFAULT_URL)) 
               
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Interactions(bot))