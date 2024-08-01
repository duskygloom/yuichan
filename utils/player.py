import random

from typing import Callable

from discord import VoiceClient
from discord import FFmpegPCMAudio

from utils.song import *


class Player:
    client: VoiceClient = None
    current: int = -1
    playlist: list[Song] = []
    loop: bool = False
    repeat: bool = False

    def __init__(self, client: VoiceClient):
        self.client = client

    def go_prev(self):
        if self.repeat:
            return
        self.current -= 1
        if self.loop and self.current < 0:
            self.current = len(self.playlist) - 1

    def go_next(self):
        if self.repeat:
            return
        self.current += 1
        if self.loop and self.current >= len(self.playlist):
            self.current = 0

    def add_to_playlist(self, songs: list[Song]):
        self.playlist.extend(songs)

    def play(self, callback: Callable = None):
        if self.current < 0 and self.current >= len(self.playlist):
            return
        callback = self.play_next
        self.client.play(FFmpegPCMAudio(self.playlist[self.current].path), after=callback)
    
    def play_prev(self, callback: Callable = None):
        self.go_prev()
        self.play()

    def play_next(self, callback: Callable = None):
        self.go_next()
        self.play()

    def shuffle(self):
        random.shuffle(self.playlist)
        self.current = 0

    def get_current(self) -> Song | None:
        if self.current < 0 or self.current >= len(self.playlist):
            return None
        return self.playlist[self.current]
    

__all__ = ["Player"]
