import random

from typing import Callable

from discord import VoiceClient
from discord import FFmpegPCMAudio


class Song:
    path: str
    title: str
    source: str
    thumbnail: str

    @staticmethod
    def create_brief(path: str) -> "Song":
        song = Song()
        song.path = path
        return song


class Player:
    client: VoiceClient = None
    current: int = -1
    playlist: list[Song] = []
    loop: bool = False
    repeat: bool = False

    def __init__(self, client: VoiceClient):
        self.client = client

    def _prev(self):
        if self.repeat:
            return
        self.current -= 1
        if self.loop and self.current < 0:
            self.current = len(self.playlist) - 1

    def _next(self):
        if self.repeat:
            return
        self.current += 1
        if self.loop and self.current >= len(self.playlist):
            self.current = 0

    def add_to_playlist(self, song: Song):
        self.playlist.append(song)

    def play(self, callback: Callable = None):
        if self.current < 0 and self.current >= len(self.playlist):
            return
        self.client.play(FFmpegPCMAudio(self.playlist[self.current].path), after=callback)
    
    def play_prev(self, callback: Callable = None):
        self._prev()
        self.play(callback)

    def play_next(self, callback: Callable = None):
        self._next()
        self.play(callback)

    def shuffle(self):
        random.shuffle(self.playlist)
        self.current = 0


__all__ = ["Player", "Song"]
