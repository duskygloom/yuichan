import asyncio

from discord import Guild
from discord import Status
from discord import Intents
from discord import VoiceClient
from discord import VoiceProtocol
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


class VoiceBot(commands.Bot):
    voice_protocol: dict[Guild, VoiceProtocol] = {}
    players: dict[Guild, Player] = {}
    '''
    Note
    ----
    `context` is used when overriding `close()`
    '''
    context: commands.Context = None

    def __init__(self):
        secret = load_secret()
        super().__init__(
            command_prefix=secret['bot_prefix'],
            intents=Intents.all()
        )

    def is_connected(self, guild: Guild) -> bool:
        '''
        Returns
        -------
        Returns True if bot is connected to `voice_protocol`, else returns False.

        Warning
        -------
        Does not check if `voice_protocol` is None. Ensure it is not None.
        '''
        for vc in self.voice_clients:
            if vc.channel == self.voice_protocol[guild].channel:
                return True
        return False
    
    async def leave_voice_channel(self, vc: VoiceProtocol, guild: Guild):
        '''
        Warning
        -------
        Does not check if bot is connected to `vc`. Ensure that it is by using
        `bot.is_connected`.
        '''
        await vc.disconnect()
        vc.cleanup()
        self.voice_protocol.pop(guild, None)

    async def create_player(self, guild: Guild):
        client = await self.get_voice_client(guild)
        if not client:
            return
        self.players[guild] = Player(client)
    
    def delete_player(self, guild: Guild):
        player = self.players.get(guild)
        if not player:
            return
        if player.client.is_playing():
            player.client.pause()
        player.client.stop()
        self.players.pop(guild, None)

    async def on_ready(self):
        secret = load_secret()
        for cog in secret['cogs']:
            await self.load_extension(cog)
            logger.info(f"Loaded extension: {cog}")
        await self.change_presence(status=status, activity=activity)

    async def get_voice_client(self, guild: Guild) -> VoiceClient | None:
        '''
        Returns
        -------
        Returns voice client corresponding to `voice_protocol` and None if `voice_protocol`
        does not exist for `guild`.
        '''
        if not self.voice_protocol.get(guild):
            return None
        for vc in self.voice_clients:
            if vc.channel == self.voice_protocol[guild].channel:
                return vc
        return None
    
    async def close(self):
        voice_clients: list[VoiceClient] = self.voice_clients
        for vc in voice_clients:
            if vc.is_playing():
                vc.pause()
            vc.play(FFmpegPCMAudio("assets/shutdown.m4a"))
        for vc in voice_clients:
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
            await vc.disconnect()
            vc.cleanup()
        if self.context:
            await self.context.reply("Shutting down.")
        await super().close()


__all__ = ["VoiceBot"]
