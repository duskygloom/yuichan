import asyncio
from enum import Enum
from typing import Coroutine

from discord import Guild
from discord import Status
from discord import Intents
from discord import VoiceClient
from discord import VoiceChannel
from discord import CustomActivity
from discord import FFmpegPCMAudio

from discord.ext import commands

from utils.logger import *
from utils.player import *
from utils.secret import *

logger = get_logger(__name__)

secret = load_secret()

status = Status.online
activity = CustomActivity(f"{secret['custom_activity']['activity']} {secret['custom_activity']['emoji']}")


class VoiceConnectionStatus(Enum):
    OK = 0
    ALREADY_CONNECTED = 1
    NOT_IN_GUILD = 2


class VoiceBot(commands.Bot):
    '''
    Attributes
    ----------
    `context`: Used in `bot.close()` to store the last context.

    `players`: Keeps track of voice clients in different guilds.
    '''
    context: commands.Context = None
    players: dict[Guild, Player] = {}

    def __init__(self):
        secret = load_secret()
        super().__init__(
            command_prefix=secret['bot_prefix'],
            intents=Intents.all()
        )

    def is_connected(self, guild: Guild) -> bool:
        '''
        Description
        -----------
        Returns True if Yui is connected to any voice channel in the 
        guild else returns False. Voice channel is stored in `players`.
        '''
        # if not in player
        guild_voice_channels = guild.voice_channels
        if guild not in self.players:
            for vc in self.voice_clients:
                if vc.channel in guild_voice_channels:
                    self.players[guild] = Player(vc)
                    return True
            return False
        # check in voice clients
        for vc in self.voice_clients:
            if vc.channel == self.players[guild].client.channel:
                return True
        # remove guild from player if not in voice_clients
        self.players.pop(guild, None)
        return False
    
    async def connect_voice(self, guild: Guild, voice_channel: VoiceChannel) -> Coroutine[None, None, VoiceConnectionStatus]:
        # if already connected
        if self.is_connected(guild):
            return VoiceConnectionStatus.ALREADY_CONNECTED
        # if voice channel not in guild
        if voice_channel not in guild.voice_channels:
            return VoiceConnectionStatus.NOT_IN_GUILD
        # connect
        client = await voice_channel.connect()
        self.players[guild] = Player(client)
        return VoiceConnectionStatus.OK
    
    async def disconnect_voice(self, guild: Guild) -> Coroutine[None, None, bool]:
        '''
        Description
        -----------
        Disconnects from any voice channel Yui is connected to. Returns
        False if not connected with any voice channel, else returns True.
        '''
        # if not connected
        if not self.is_connected(guild):
            return False
        client = self.players[guild].client
        # pause client
        if client.is_playing():
            client.pause()
        # disconnect
        await client.disconnect()
        client.cleanup()
        # remove from players
        self.players.pop(guild, None)
        return True

    async def on_ready(self):
        secret = load_secret()
        for cog in secret['cogs']:
            await self.load_extension(cog)
            logger.info(f"Loaded extension: {cog}")
        await self.change_presence(status=status, activity=activity)

    def get_voice_client(self, guild: Guild) -> VoiceClient | None:
        '''
        Returns
        -------
        If Yui is connected to any voice channel in the guild,
        returns the voice channel, else returns None.
        '''
        if not self.is_connected(guild):
            return None
        return self.players[guild].client
    
    async def close(self):
        # play shutdown tone in every active voice client
        voice_clients: list[VoiceClient] = self.voice_clients
        for vc in voice_clients:
            if vc.is_playing():
                vc.pause()
            vc.play(FFmpegPCMAudio("assets/shutdown.m4a"))
        # wait for shutdown tone to finish and disconnect
        # from each voice channel
        for vc in voice_clients:
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
            await vc.disconnect()
            vc.cleanup()
        # shutdown
        if self.context:
            await self.context.reply("Shutting down.")
        await super().close()


__all__ = ["VoiceBot", "VoiceConnectionStatus"]
