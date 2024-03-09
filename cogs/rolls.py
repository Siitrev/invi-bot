import discord, re, math, random
from discord.ext import commands
from discord import app_commands

ERROR_TEXTS = [
    "No podałeś błędną wartość no brawo. Dumny z siebie jesteś?",
    "Chcesz mnie zabić, że taki rzut podajesz???",
    "Co ja ci zrobilem...",
    "Ja rozumiem, że niektórzy są specjalni, ale bez przesady :face_with_raised_eyebrow:",
    "Dobrze sie bawisz?",
    "A wiedziałeś, że koale mają gładki mózg? Nie masz na pewno z nimi nic wspólnego?",
    "Ale poddymianie :sunglasses:",
    "Ja jestem zapracowany, a ty mi jeszcze roboty dokładasz....",
    "Pamiętaj zwolnij troszeczke, nic cie nie zabije, nie ma potrzeby robic bledu w komendzie",
    "Moze powinienem zrobic licznik ile razy popełniłeś błąd",
    "Ej ale szczerze to bardzo dobrze ci idzie, liczą się chęci",
    "Nienawidze wiadomo czego i wiadomo kogo",
    "Prosze cie zeby to był twój ostatni raz...",
    "Matko jedyna, nie no siwy dym idziesz do domu",
]

SUCCESS_TEXTS = [
    "Mam nadzieje, że to był krytyczny pech...",
    "Na pewno rozbroiłeś tą pułapkę, na 100%",
    "EJ NIE IDŹ W STRONE ŚWIATŁA",
    ":point_right: :point_left: :face_holding_back_tears:",
    "Ale to był rzut :eye: :biting_lip: :eye:",
    "Ciekawostka: w warhammerze jest bardzo łatwo umrzeć czy to choroba, chaos, zwierzoludzie, bandyci, \
      rózne inne monstra, pogoda, urwiska, króliczki, trolle, komornicy, potknięcia, menele, złe składniki alchemiczne, spaleni ludzie i wiele wiele innych...",
    "Mordeczko, ale ostre kości zostały rzucone :call_me: :sunglasses: ",
    "Siała baba mak, nie wiedziała jak, a dziad wiedział, nie powiedział, a to było tak...",
    "Gejmaster ma zawsze racje, nie możesz sie z nim kłócić i sprzeciwiać jego poleceniom :point_up::nerd:",
    "Wiedziałeś, że krasnoludy wpisały do księgi uraz nawet górę?",
    "Trudne sie wylosowało..."
]

SUCC_EMBED = discord.Embed(title="Tajemny rzut poszedł do gejmastera!", color=discord.Color.green())
ERR_EMBED = discord.Embed(title="Błąd!", color=discord.Color.red())

class Rolls(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ukryty-rzut", description="Zakrec koscia wariacik")
    @app_commands.describe(roll="Podaj ilość oraz kość. Poprawny format to [ile razy][k|d][ilość ścian kości]")
    async def dolacz(self, interaction: discord.Interaction, roll: str) -> None:
        text_channel = discord.utils.get(interaction.guild.text_channels, name="ukryty-rzut")
        pattern = re.compile(r"^\d+[kd]\d+$", re.IGNORECASE)
        is_vaild = re.match(pattern, roll)
        
        ERR_EMBED.description = random.choice(ERROR_TEXTS)
        SUCC_EMBED.description = random.choice(SUCCESS_TEXTS)

        if not is_vaild:
            await interaction.response.send_message(embed=ERR_EMBED)
            return
        
        roll = roll.lower()
        if roll.find("d") != -1:
            rolls = roll.split("d")
        else:
            rolls = roll.split("k")
        
        amount = int(rolls[0])
        dice = int(rolls[1])

        if dice > 10000 or dice < 2:
            await interaction.response.send_message(embed=ERR_EMBED)
            return
        
        if amount > 100 or amount < 1:
            await interaction.response.send_message(embed=ERR_EMBED)
            return
        
        s = 0
        separate_rolls = []
        
        for _ in range(amount):
            dice_num = random.randint(1, dice)
            s += dice_num
            separate_rolls.append(dice_num)
            
        nick = interaction.user.nick

        modifier = math.ceil(dice*0.04)
        
        for ind, r in enumerate(separate_rolls):
            if r == 1:
                separate_rolls[ind] = f"\u001b[0;32m{r}\u001b[0;0m"
            elif r >= dice-modifier:
                separate_rolls[ind] = f"\u001b[0;31m{r}\u001b[0;0m"
            else:
                separate_rolls[ind] = f"\u001b[0;37m{r}\u001b[0;0m"


        final_message = f"""
        ```ansi
        Gracz: {nick}
        Rzut: {roll}
        Wyrzucił: {s}
        Rzuty, które wypadły to:
        """  

        if amount > 15:
            for i in range(15, amount, 15):
                final_message += ("  ".join(separate_rolls[i-15:i])) + "\n\t\t"
        else:
            final_message += ("  ".join(separate_rolls)) 
        
        final_message += "```"

        await text_channel.send(final_message)
        await interaction.response.send_message(embed=SUCC_EMBED)
            
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