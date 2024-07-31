import os

from utils.secret import *

secret = load_secret()


class Song:
    id: str = ""
    url: str = ""
    path: str = ""
    title: str = ""
    artist: str = ""
    duration: int = 0
    thumbnail: str = ""

    def duration_str(self) -> str:
        text = f"{int(self.duration // 60)} mins {int(self.duration % 60)} secs"
        return text

    def exists(self) -> bool:
        return os.path.exists(self.path)
    
    def __str__(self) -> str:
        return self.id

    @staticmethod
    def from_info(info: dict, complete: bool = False):
        song = Song()
        song.id = info.get("id")
        song.url = info.get("url") or info("original_url")
        song.title = info.get("title")
        song.duration = info.get("duration") or 0
        song.artist = info.get("channel")
        song.thumbnail = info.get("thumbnails")[-1].get("url")
        song.path = os.path.join(secret["download_path"], f"{song.id}.{secret['extension']}")
        if complete:
            song.source = get_source_url(info)
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
