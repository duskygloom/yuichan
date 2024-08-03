from typing import Optional

from utils import messages
from utils.bot import *
from utils.logger import *
from utils.player import *

from discord import VoiceChannel
from discord.ext import commands

logger = get_logger(__name__)


class General(commands.Cog):
    def __init__(self, bot: VoiceBot):
        self.bot = bot

    @commands.command(
        name="join",
        brief="Yui joins your voice channel."
    )
    async def join(self, ctx: commands.Context, voice_channel: Optional[VoiceChannel]):
        '''
        Description
        -----------
        If `voice_channel` is specified, Yui tries to enter the channel (author 
        must be part of the guild and must have permissions to enter voice channels),
        else tries to join the voice channel of the author.
        '''
        # check guild
        if ctx.guild is None:
            await ctx.reply(messages.guild_only_command)
            return
        # check voice permission
        if not ctx.author.guild_permissions.connect:
            await ctx.reply(messages.missing_permissions.format("connect"))
            return
        # connect
        status: VoiceConnectionStatus = await self.bot.connect_voice(ctx.guild, voice_channel)
        # if connected successfully
        if status == VoiceConnectionStatus.OK:
            await ctx.reply(messages.joined_voice_channel)
            client = self.bot.get_voice_client(ctx.guild)
            logger.info(f"Joined: {ctx.guild.name}/{client.channel.name}")
        # if already connected to a voice channel
        elif status == VoiceConnectionStatus.ALREADY_CONNECTED:
            await ctx.reply(messages.already_in_a_voice_channel)
        # if voice channel is not in guild
        elif status == VoiceConnectionStatus.NOT_IN_GUILD:
            await ctx.reply(messages.voice_channel_not_found)

    @commands.command(
        name="leave",
        brief="Yui leaves your voice channel."
    )
    async def leave(self, ctx: commands.Context):
        '''
        Description
        -----------
        Leave the stored voice channel. If no voice channel is stored leave
        from any voice channel the bot is connected to in the guild.
        '''
        # check guild
        if ctx.guild is None:
            await ctx.reply(messages.guild_only_command)
            return
        # check voice permission
        if not ctx.author.guild_permissions.connect:
            await ctx.reply(messages.missing_permissions.format("connect"))
            return
        # disconnect
        status: bool = await self.bot.disconnect_voice(ctx.guild)
        if status:
            await ctx.reply(messages.left_voice_channel)
            logger.info(f"Left voice channel in guild: {ctx.guild.name}")
        else:
            await ctx.reply(messages.not_in_voice_channel)


async def setup(bot: VoiceBot):
    await bot.add_cog(General(bot))
