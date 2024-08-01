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

    async def _enqueue(self, ctx: commands.Context, song: str) -> Player | None:
        secret = load_secret()
        # check if personal command
        if not ctx.guild:
            await ctx.reply(messages.guild_only_command)
            return None
        # check if connected to voice channel
        if self.bot.voice_protocol.get(ctx.guild) is None:
            await ctx.reply(messages.not_in_voice_channel)
            return None
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await self.bot.create_player(ctx.guild)
            player = self.bot.players[ctx.guild]
        # add to playlist
        await ctx.message.add_reaction(secret["emojis"]["search"])
        songs: list[Song] = await self.bot.loop.run_in_executor(None, partial(search_songs, song))
        player.add_to_queue(songs)
        player.current = len(player.queue) - len(songs)
        await ctx.message.remove_reaction(secret["emojis"]["search"], self.bot.user)
        return player

    @commands.command(
        name="play",
        brief="Yui plays the song you request."
    )
    async def play(self, ctx: commands.Context, song: str):
        player = await self._enqueue(ctx, song)
        if not player:
            return
        # if another song playing
        if player.client.is_playing():
            player.client.pause()
        # play
        player.is_playing = True
        while player.is_playing:
            await player.play(ctx)
    
    @commands.command(
        name="enqueue",
        brief="Yui adds the song you request to queue."
    )
    async def enqueue(self, ctx: commands.Context, song: str):
        await self._enqueue(ctx, song)

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
    
    @commands.command(
        name="resume",
        brief="Yui resumes the currently paused song."
    )
    async def pause(self, ctx: commands.Context):
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await ctx.reply(messages.no_player_found)
            return
        # if playing
        if player.client.is_playing():
            await ctx.reply(messages.player_not_paused)
            return
        # pause
        player.client.resume()

    @commands.command(
        name="next",
        brief="Yui plays the next song in the queue."
    )
    async def next(self, ctx: commands.Context):
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await ctx.reply(messages.no_player_found)
            return
        # if playing
        if player.client.is_playing():
            player.pause()
        # play next
        player.go_next()
        await player.play(ctx)
    
    @commands.command(
        name="prev",
        brief="Yui plays the previous song in the queue."
    )
    async def prev(self, ctx: commands.Context):
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await ctx.reply(messages.no_player_found)
            return
        # if playing
        if player.client.is_playing():
            player.pause()
        # play prev
        player.go_prev()
        await player.play(ctx)

    @commands.command(
        name="queue",
        brief="Yui shows the list of songs in the queue."
    )
    async def queue(self, ctx: commands.Context):
        # obtain player
        player = self.bot.players.get(ctx.guild)
        if not player:
            await ctx.reply(messages.no_player_found)
            return
        # message
        message = '\n'.join([f"**{song.title}** [*{song.artist}*]" for song in player.queue])
        await ctx.reply(message)


async def setup(bot: VoiceBot):
    await bot.add_cog(Music(bot))
