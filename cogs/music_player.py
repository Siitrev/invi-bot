import discord, lavalink, re, logging
from discord.ext import commands
from discord import app_commands
from lavalink import LoadType
from common.settings import LAVALINK_PASSWORD

url_rx = re.compile(r'https?://(?:www\.)?.+')
_log = logging.getLogger(__name__)

class MusicPlayer(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        if not hasattr(bot, 'lavalink') or bot.lavalink is None:
            self.bot.lavalink = lavalink.Client(bot.user.id)
            self.bot.lavalink.add_node(
                host="lavalink",
                port=2333,
                password=LAVALINK_PASSWORD,
                region="eu",
                name="phantom-bot-node"
            )

        self.lavalink = self.bot.lavalink
        self.lavalink.add_event_hooks(self)

    async def create_player(interaction: discord.Interaction):
        """
        This function will try to create a player for the guild associated with this Context, or raise
        an error which will be relayed to the user if one cannot be created.
        """
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage()

        player: lavalink.DefaultPlayer = interaction.client.lavalink.player_manager.create(interaction.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = interaction.command.name in ('play',)

        voice_client = interaction.guild.voice_client

        if not interaction.user.voice or not interaction.user.voice.channel:
            if voice_client is not None:
                raise app_commands.CommandInvokeError('You need to join my voice channel first.')

            raise app_commands.CommandInvokeError('Join a voicechannel first.')

        voice_channel = interaction.user.voice.channel

        if voice_client is None:
            if not should_connect:
                raise app_commands.CommandInvokeError("I'm not playing music.")

            bot_member = interaction.guild.get_member(interaction.client.user.id)
            permissions = voice_channel.permissions_for(bot_member)

            if not permissions.connect or not permissions.speak:
                raise app_commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')

            if voice_channel.user_limit > 0:
                # A limit of 0 means no limit. Anything higher means that there is a member limit which we need to check.
                # If it's full, and we don't have "move members" permissions, then we cannot join it.
                if len(voice_channel.members) >= voice_channel.user_limit and not interaction.guild.me.guild_permissions.move_members:
                    raise app_commands.CommandInvokeError('Your voice channel is full!')

            player.store('channel', interaction.channel.id)
            await interaction.user.voice.channel.connect(cls=LavalinkVoiceClient)
        elif voice_client.channel.id != voice_channel.id:
            raise app_commands.CommandInvokeError('You need to be in my voicechannel.')

        return True

    @app_commands.command(name="play", description="Zagraj muzyczke")
    @app_commands.describe(url="Link do piosenki")
    @app_commands.check(create_player)
    async def play(self, interaction: discord.Interaction, url: str) -> None:   
        player: lavalink.DefaultPlayer = self.bot.lavalink.player_manager.get(interaction.guild_id)
        
        query = url.strip('<>')
        
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        
        results = await player.node.get_tracks(query)
        
        embed = discord.Embed(color=discord.Color.blurple())
        
        if results.load_type == LoadType.EMPTY:
            return await interaction.response.send_message("I couldn'\t find any tracks for that query.")
        elif results.load_type == LoadType.PLAYLIST:
            tracks = results.tracks

            for track in tracks:
                # requester isn't necessary but it helps keep track of who queued what.
                # You can store additional metadata by passing it as a kwarg (i.e. key=value)
                # Requester can be set with `track.requester = ctx.author.id`. Any other extra attributes
                # must be set via track.extra.
                track.extra["requester"] = interaction.user.id
                player.add(track=track)

            embed.title = 'Playlist Enqueued!'
            embed.description = f'{results.playlist_info.name} - {len(tracks)} tracks'
        else:
            track = results.tracks[0]
            embed.title = 'Track Enqueued'
            embed.description = f'[{track.title}]({track.uri})'

            # requester isn't necessary but it helps keep track of who queued what.
            # You can store additional metadata by passing it as a kwarg (i.e. key=value)
            # Requester can be set with `track.requester = ctx.author.id`. Any other extra attributes
            # must be set via track.extra.
            track.extra["requester"] = interaction.user.id

            player.add(track=track)

        await interaction.response.send_message(embed=embed)

        if not player.is_playing:
            await player.play()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicPlayer(bot))

class LavalinkVoiceClient(discord.VoiceClient):
    """
    A voice client for Lavalink.
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.guild_id = channel.guild.id
        self._destroyed = False
        if not hasattr(self.client, 'lavalink') or self.client.lavalink is None:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                host="lavalink",
                port=2333,
                password=LAVALINK_PASSWORD,
                region="eu",
                name="phantom-bot-node")

        self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        channel_id = data['channel_id']

        if not channel_id:
            await self._destroy()
            return

        self.channel = self.client.get_channel(int(channel_id))

        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }

        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        if not force and not player.is_connected:
            return

        await self.channel.guild.change_voice_state(channel=None)

        player.channel_id = None
        await self._destroy()
        
    async def _destroy(self):
        self.cleanup()

        if self._destroyed:
            return

        self._destroyed = True

        try:
            await self.lavalink.player_manager.destroy(self.guild_id)
        except lavalink.ClientError:
            pass