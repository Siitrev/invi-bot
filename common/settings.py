import environ, os

env = environ.Env()
env.read_env(".env")

LAVALINK_PASSWORD = os.environ.get("LAVALINK_PASSWORD")
TOKEN = os.environ.get("DISCORD_TOKEN")
APP_ID = os.environ.get("APP_ID")
DEFAULT_GIF_URL = "https://cdn.discordapp.com/attachments/720181859182706711/1397638120760934420/hop-on-roll20.gif?ex=6882736e&is=688121ee&hm=b3c53a847ebccda7b3dc5ef9ac06357710314780b902ac792193b705f37d5282&"
DEFAULT_URL = "https://app.roll20.net/join/18778491/A34BBw"
