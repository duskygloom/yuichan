from typing import Optional

from utils import messages
from utils.bot import *
from utils.logger import *

from discord import VoiceChannel
from discord.ext import commands

logger = get_logger(__name__)


class General(commands.Cog):
    def __init__(self, bot: VoiceBot):
        self.bot = bot

    @commands.command(
        name="join",
        description="Yui joins your voice channel."
    )
    async def join(self, ctx: commands.Context, voice_channel: Optional[VoiceChannel]):
        '''
        Description
        -----------
        If `voice_channel` is specified, yuichan tries to enter the channel (author 
        must be part of the guild and must have permissions to enter voice channels),
        else tries to join the voice channel of the author.
        '''
        if ctx.guild is None:
            await ctx.reply(messages.guild_only_command)
            return
        if not ctx.author.guild_permissions.connect:
            await ctx.reply(messages.missing_permissions.format("connect"))
            return
        if not voice_channel:
            if not ctx.author.voice:
                await ctx.reply(messages.user_not_in_voice_channel)
                return
            voice_channel = ctx.author.voice.channel
        if voice_channel not in ctx.guild.voice_channels:
            await ctx.reply(messages.voice_channel_not_found)
            return
        for vc in self.bot.voice_clients:
            if vc.channel == voice_channel:
                await ctx.reply(messages.already_in_voice_channel)
                return
            if vc.channel in ctx.guild.voice_channels:
                await ctx.reply(messages.present_in_voice_channel)
                return
        self.bot.voice_protocol[ctx.guild] = await voice_channel.connect()

    @commands.command(
        name="leave",
        description="Yui leaves your voice channel."
    )
    async def leave(self, ctx: commands.Context):
        '''
        Description
        -----------
        Attemps to leave voice channel stored in `bot.voice_protocol`.
        If unsuccessful, attemps to leave from any voice channel bot
        is connected to in the guild.
        '''
        if ctx.guild is None:
            await ctx.reply(messages.guild_only_command)
            return
        voice_protocol = self.bot.voice_protocol.get(ctx.guild)
        if not voice_protocol:
            await ctx.reply(messages.not_in_voice_channel)
            return
        if not ctx.author.guild_permissions.connect:
            await ctx.reply(messages.missing_permissions.format("connect"))
            return
        if self.bot.is_connected(ctx.guild):
            await self.bot.leave_voice_channel(voice_protocol, ctx.guild)
            logger.info(f"Left voice channel in guild: {ctx.guild.name}")
            self.bot.voice_protocol.pop(ctx.guild, None)
            await ctx.reply(messages.left_voice_channel)
            return
        for vc in self.bot.voice_clients:
            if vc.channel in ctx.guild.voice_channels:
                self.bot.leave_voice_channel(vc, ctx.guild)
                logger.info(f"Left voice channel in guild: {ctx.guild.name}")
                await ctx.reply(messages.left_voice_channel)
                return


async def setup(bot: VoiceBot):
    await bot.add_cog(General(bot))
