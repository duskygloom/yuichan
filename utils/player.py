import random

from typing import Callable
from discord import VoiceClient
from discord import FFmpegPCMAudio
from functools import partial
from discord.ext import commands

from utils.song import *
from utils.secret import *
from utils.downloader import *


class Player:
    client: VoiceClient = None
    current: int = -1
    queue: list[Song] = []
    loop: bool = False
    repeat: bool = False
    '''
    Note
    ----
    Not to be confused with `client.is_playing()`.
    `is_playing` is used to manually check when to stop playing.
    '''
    is_playing: bool = False

    def __init__(self, client: VoiceClient):
        self.client = client

    def go_prev(self):
        if self.repeat:
            return
        self.current -= 1
        if self.loop and self.current < 0:
            self.current = len(self.queue) - 1

    def go_next(self):
        if self.repeat:
            return
        self.current += 1
        if self.loop and self.current >= len(self.queue):
            self.current = 0

    def add_to_queue(self, songs: list[Song]):
        self.queue.extend(songs)

    async def play(self, ctx: commands.Context, callback: Callable = None):
        if self.get_current() is None:
            return
        # download
        secret = load_secret()
        await ctx.message.add_reaction(secret["emojis"]["download"])
        bot: commands.Bot = ctx.bot
        await bot.loop.run_in_executor(None, clear_downloads)
        await bot.loop.run_in_executor(None, partial(download_song, self.get_current()))
        await ctx.message.remove_reaction(secret["emojis"]["download"], ctx.bot.user)
        # play
        callback = lambda *_: self.go_next()
        self.client.play(FFmpegPCMAudio(self.queue[self.current].path), after=callback)

    def pause(self):
        self.is_playing = False
        super().pause()
    
    def shuffle(self):
        random.shuffle(self.queue)
        self.current = 0

    def get_current(self) -> Song | None:
        if self.current < 0 or self.current >= len(self.queue):
            return None
        return self.queue[self.current]


__all__ = ["Player"]
