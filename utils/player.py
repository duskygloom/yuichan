import random

from enum import Enum
from typing import Callable
from discord import VoiceClient
from discord import FFmpegPCMAudio
from discord import PCMVolumeTransformer
from functools import partial
from discord.ext import commands

from utils.song import *
from utils.secret import *
from utils.downloader import *


class PlayStatus(Enum):
    OK = 0
    EMPTY_QUEUE = 1
    NO_NEXT_SONG = 2
    NO_SONG_FOUND = 3


class Player:
    queue: list[Song] = []
    client: VoiceClient
    source: PCMVolumeTransformer = None
    volume: int = 50
    current: int
    loop: bool = False
    repeat: bool = False

    def __init__(self, client: VoiceClient):
        self.client = client

    def _prev(self) -> bool:
        '''
        Note
        ----
        Ensure queue is not empty.
        '''
        # if current is not set yet
        if not hasattr(self, "current"):
            return True
        # if repeat mode
        if self.repeat:
            return True
        # if loop mode
        if self.loop and self.current <= 0:
            self.current = len(self.queue) - 1
            return True
        # if there is previous song
        elif self.current > 0:
            self.current -= 1
            return True
        # cannot go to previous song
        return False

    def _next(self) -> bool:
        '''
        Note
        ----
        Ensure queue is not empty.
        '''
        # if current is not set yet
        if not hasattr(self, "current"):
            return False
        # if repeat mode
        if self.repeat:
            return True
        # if loop mode
        if self.loop and self.current >= len(self.queue) - 1:
            self.current = 0
            return True
        # if there is next song
        elif self.current < len(self.queue) - 1:
            self.current += 1
            return True
        # cannot go to next song
        return False
    
    def append(self, songs: list[Song]):
        if not hasattr(self, "current") and len(songs) > 0:
            self.current = 0
        self.queue.extend(songs)
    
    def insert(self, songs: list[Song]):
        if not hasattr(self, "current") and len(songs) > 0:
            self.current = 0
            self.append(songs)
            return
        self.queue = self.queue[ : self.current] + songs + self.queue[self.current : ]
    
    def play(self) -> PlayStatus:
        '''
        Description
        -----------
        Creates source of the current song and stores in `source`.
        '''
        # if queue empty
        if len(self.queue) == 0:
            return PlayStatus.EMPTY_QUEUE
        # if no next song
        if self._next() == False:
            return PlayStatus.NO_NEXT_SONG
        # if song is not found
        if self.queue[self.current].exists() == False:
            return PlayStatus.NO_SONG_FOUND
        # play next song
        self.source = PCMVolumeTransformer(FFmpegPCMAudio(self.queue[self.current].path), volume=self.volume/100)
        return PlayStatus.OK
    
    def stop(self):
        delattr(self, "current")
    
    def get_current(self) -> Song | None:
        if not hasattr(self, "current"):
            return None
        return self.queue[self.current]


__all__ = ["Player", "PlayStatus"]
