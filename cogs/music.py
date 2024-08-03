import asyncio

from functools import partial
from discord.ext import commands

from utils import messages
from utils.bot import *
from utils.song import *
from utils.logger import *
from utils.player import *
from utils.secret import *
from utils.downloader import *

logger = get_logger(__name__)


class Music(commands.Cog):
    def __init__(self, bot: VoiceBot):
        self.bot = bot

    async def _play_current(self, ctx: commands.Context):
        '''
        Note
        ----
        Ensure player exists for guild.
        '''
        secret = load_secret()
        player = self.bot.players[ctx.guild]
        # download song
        await ctx.message.add_reaction(secret["emojis"]["download"])
        await self.bot.loop.run_in_executor(None, partial(download_song, player.get_current()))
        await ctx.message.remove_reaction(secret["emojis"]["downlaod"], self.bot.user)
        # play song
        status = player.play()
        if status == PlayStatus.OK:
            if player.client.is_playing():
                player.client.pause()
            player.client.play(player.source)
            await ctx.reply(f"Playing {player.get_current()}.")
            # play again after song has finished playing
            while player.client.is_playing():
                await asyncio.sleep(1)
            await self._play_current(ctx)
        elif status == PlayStatus.EMPTY_QUEUE:
            await ctx.reply(messages.empty_queue)
        elif status == PlayStatus.NO_NEXT_SONG:
            await ctx.reply(messages.no_next_song)
        elif status == PlayStatus.NO_SONG_FOUND:
            await ctx.reply(messages.no_song_found)

    @commands.command(
        name="play",
        brief="Yui plays the specified song(s)."
    )
    async def _play(self, ctx: commands.Context, query: str):
        # if player not created
        if not self.bot.players.get(ctx.guild):
            await ctx.reply(messages.not_in_voice_channel)
            return
        # search songs
        secret = load_secret()
        await ctx.message.add_reaction(secret["emojis"]["search"])
        songs: list[Song] = await self.bot.loop.run_in_executor(None, partial(search_songs, query))
        await ctx.message.remove_reaction(secret["emojis"]["search"], self.bot.user)
        self.bot.players[ctx.guild].insert(songs)
        await ctx.reply(f"Added {len(songs)} songs.")
        # play current song
        await self._play_current()
        

    @commands.command(
        name="enqueue",
        brief="Yui adds the specified song(s) to the queue."
    )
    async def _enqueue(self, ctx: commands.Context, query: str):
        ...

    @commands.command(
        name="stop",
        brief="Yui stops playing songs."
    )
    async def _stop(self, ctx: commands.Context):
        ...

    @commands.command(
        name="pause",
        brief="Yui pauses the currently playing song."
    )
    async def _pause(self, ctx: commands.Context):
        ...

    @commands.command(
        name="resume",
        brief="Yui resumes the currently paused song."
    )
    async def _resume(self, ctx: commands.Context):
        ...

    @commands.command(
        name="next",
        brief="Yui plays the next song."
    )
    async def _next(self, ctx: commands.Context):
        ...

    @commands.command(
        name="prev",
        brief="Yui plays the previous song."
    )
    async def _prev(self, ctx: commands.Context):
        ...

    @commands.command(
        name="jump",
        brief="Yui jumps to the specified song."
    )
    async def _jump(self, ctx: commands.Context, index: int):
        ...


async def setup(bot: VoiceBot):
    await bot.add_cog(Music(bot))
