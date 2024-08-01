from functools import partial
from discord.ext import commands

from utils import messages
from utils.bot import *
from utils.song import *
from utils.logger import *
from utils.secret import *
from utils.downloader import *

logger = get_logger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: VoiceBot):
        self.bot = bot

    @commands.command(
        name="play",
        brief="Yui plays the song you request."
    )
    async def play(self, ctx: commands.Context, song: str):
        secret = load_secret()
        # check if personal command
        if not ctx.guild:
            await ctx.reply(messages.guild_only_command)
            return
        # check if connected to voice channel
        if self.bot.voice_protocol.get(ctx.guild) is None:
            await ctx.reply(messages.not_in_voice_channel)
            return
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await self.bot.create_player(ctx.guild)
            player = self.bot.players[ctx.guild]
            if not player:
                await ctx.reply(messages.not_in_voice_channel)
        # search
        await ctx.message.add_reaction(secret["emojis"]["search"])
        songs: list[Song] = await self.bot.loop.run_in_executor(None, partial(search_songs, song))
        player.add_to_playlist(songs)
        player.current = len(player.playlist) - len(songs)
        await ctx.message.remove_reaction(secret["emojis"]["search"], self.bot.user)
        # download
        await ctx.message.add_reaction(secret["emojis"]["download"])
        await self.bot.loop.run_in_executor(None, clear_downloads)
        status: bool = await self.bot.loop.run_in_executor(None, partial(download_song, player.get_current()))
        await ctx.message.remove_reaction(secret["emojis"]["download"], self.bot.user)
        # if not downloaded
        if not status:
            await ctx.reply(messages.could_not_download)
            return
        # if another song playing
        if player.client.is_playing():
            player.client.pause()
        # play
        player.play()
        # download nearby songs
        if player.current + 1 < len(player.playlist):
            next_song = player.playlist[player.current + 1]
            status: bool = await self.bot.loop.run_in_executor(None, partial(download_song, next_song))
        if player.current - 1 >= 0:
            prev_song = player.playlist[player.current - 1]
            status: bool = await self.bot.loop.run_in_executor(None, partial(download_song, prev_song))

    @commands.command(
        name="pause",
        brief="Yui pauses the currently playing song."
    )
    async def pause(self, ctx: commands.Context):
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await ctx.reply(messages.no_player_found)
            return
        # if paused
        if player.client.is_paused():
            await ctx.reply(messages.player_already_paused)
            return
        # pause
        player.client.pause()


async def setup(bot: VoiceBot):
    await bot.add_cog(Music(bot))
