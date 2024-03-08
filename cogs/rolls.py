import discord, re, environ, os, random
from discord.ext import commands
from discord import app_commands

class Rolls(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ukryty-rzut", description="Zakrec koscia wariacik")
    @app_commands.describe(roll="Podaj ilość oraz kość. Poprawny format to [ile razy][k|d][ilość ścian kości]")
    async def dolacz(self, interaction: discord.Interaction, roll: str) -> None:
        text_channel = discord.utils.get(interaction.guild.text_channels, name="ukryty-rzut")
        pattern = re.compile(r"^\d+[kd]\d+$", re.IGNORECASE)
        is_vaild = re.match(pattern, roll)
        if not is_vaild:
            await interaction.response.send_message("No podałeś błędną wartość no brawo. Dumny z siebie jesteś?")
            return
        
        roll = roll.lower()
        if roll.find("d") != -1:
            rolls = roll.split("d")
        else:
            rolls = roll.split("k")
        
        amount = int(rolls[0])
        
        dice = int(rolls[1])
        if dice > 10000 or dice < 2:
            await interaction.response.send_message("Chcesz mnie zabić że taką kość podajesz???")
            return
        
        if amount > 100 or amount < 1:
            await interaction.response.send_message("Co ja ci zrobilem...")
            return
        
        s = 0
        separate_rolls = []
        
        for _ in range(amount):
            dice_num = random.randint(1, dice)
            s += dice_num
            separate_rolls.append(dice_num)
            
        nick = interaction.user.nick
        
        await text_channel.send(f"Gracz {nick} rzucił {roll} i wylosował {s}. Rzuty jakie wypadły to {separate_rolls}")
        await interaction.response.send_message("Tajemny rzut poszedł do gejmastera!")
            
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
        }
        
        text_channel = discord.utils.get(guild.text_channels, name="ukryty-rzut")
        
        if text_channel == None:
            await guild.create_text_channel(
                name="ukryty-rzut",
                topic="Czego oczy nie widzą, tego sercu nie żal...",
                overwrites=overwrites,
            )
    
		
		
        

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Rolls(bot))