import os

from utils.secret import *

secret = load_secret()


class Song:
    id: str
    url: str
    title: str
    artist: str
    duration: int
    _info: dict
    _path: str
    _thumbnail: str

    def duration_str(self) -> str:
        duration = 0
        if hasattr(self, "duration"):
            duration = self.duration
        text = f"{int(duration // 60)} minutes {int(duration % 60)} seconds"
        return text

    def exists(self) -> bool:
        return os.path.exists(self.path)
    
    @property
    def path(self):
        if hasattr(self, "_path"):
            return self._path
        return os.join(secret["download_path"], f"{self.id}.{secret['extension']}")
    
    @path.setter
    def path(self, filepath: str):
        self._path = filepath
    
    @property
    def thumbnail(self):
        if hasattr(self, "_thumbnail"):
            return self._thumbnail
        return f"https://i.ytimg.com/vi/{self.id}/hqdefault.jpg"
    
    @thumbnail.setter
    def thumbnail(self, fileurl: str):
        self._thumbnail = fileurl
    
    def __str__(self) -> str:
        secret = load_secret()
        if not hasattr(self, "title"):
            return f"**{self.path.lstrip(secret['download_path'])}**"
        elif not hasattr(self, "artist"):
            return f"**{self.title}**"
        return f"**{self.title}** [*{self.artist}*]"

    @staticmethod
    def from_info(info: dict) -> "Song":
        song = Song()
        song.id = info["id"]
        song.url = info["original_url"]
        song.title = info["title"]
        song.artist = info["uploader"]
        song.duration = info["duration"]
        return song
    
    @staticmethod
    def from_entry(entry: dict) -> "Song":
        song = Song()
        song.id = entry["id"]
        song.url = entry["url"]
        song.title = entry["title"]
        song.artist = entry["uploader"]
        song.duration = entry["duration"]
        return song
    
    @staticmethod
    def from_path(filepath: str) -> "Song":
        song = Song()
        song.path = filepath
        return song
    

def get_source_url(info: dict) -> str:
    '''
    Returns
    -------
    Returns download url of the audio or empty string if not found.
    '''
    for format in info.get("formats"):
        is_audio = format.get("acodec") != "none" and format.get("vcodec") == "none"
        is_format = format.get("ext") == secret["extension"] and format.get("format_note") == secret["quality"]
        if is_audio and is_format:
            return format.get("url")
    return ""
    

__all__ = ["Song"]
