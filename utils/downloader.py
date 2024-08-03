import os
import re

from enum import Enum
from yt_dlp import YoutubeDL
from yt_dlp.utils import UnsupportedError

from utils.song import *
from utils.logger import *
from utils.secret import *

logger = get_logger(__name__)


def get_quiet_options(forced: bool = False) -> dict:
    secret = load_secret()
    quiet_options = {
        "quiet": True,
        "no_warnings": True
    }
    if secret["quiet_ytdl"] or forced:
        return quiet_options
    return {}


def get_download_options() -> dict:
    secret = load_secret()
    options = {
        "format": f"{secret['extension']}/{secret['quality']}",
        "outtmpl": f"{secret['download_path']}/%(id)s.{secret['extension']}",
        "noplaylist": True
    }
    return options


def clear_downloads():
    secret = load_secret()
    total_size = 0
    for file in os.listdir(secret["download_path"]):
        path = os.path.join(secret["download_path"], file)
        if os.path.isfile(path):
            total_size += os.path.getsize(path)
    if total_size > secret["max_download_size"]:
        for file in os.listdir(secret["download_path"]):
            path = os.path.join(secret["download_path"], file)
            if os.path.isfile(path):
                os.remove(os.path.join(secret["download_path"], file))
                logger.warning(f"Deleted: {path}")


class URLtype(Enum):
    YT_WATCH = "youtube video"
    YT_PLAYLIST = "youtube playlist"
    OTHER = "other"
    NOT_URL = "not a url"


def analyze_url(url: str) -> URLtype:
    url_regex = "http[s]://+"
    if re.search(re.compile(url_regex), url) == None:
        return URLtype.NOT_URL
    try:
        logger.info("Analyzing URL...")
        info = YoutubeDL(get_quiet_options(True)).extract_info(url, download=False, process=False)
        logger.info("Done.")
        basename = info.get("webpage_url_basename")
        if basename == "watch":
            return URLtype.YT_WATCH
        elif basename == "playlist":
            return URLtype.YT_PLAYLIST
        return URLtype.OTHER
    except UnsupportedError:
        logger.info("Done.")
        return URLtype.OTHER


def get_songs_from_youtube(url: str) -> list[Song]:
    '''
    Note
    ----
    Make sure to handle error. This function intentionally does not take
    care of key errors.
    '''
    options = get_quiet_options()
    logger.info("Getting song from youtube...")
    info = YoutubeDL(options).extract_info(url, download=False, process=False)
    logger.info("Done.")
    songs = []
    basename = info.get("webpage_url_basename")
    if basename == "watch":
        songs.append(Song.from_info(info))
    elif basename == "playlist":
        entries = info["entries"]
        while True:
            try:
                entry = next(entries)
                songs.append(Song.from_entry(entry))
            except StopIteration:
                break
    return songs


def search_songs_from_youtube(query: str) -> list[Song]:
    '''
    Note
    ----
    Make sure to handle error. This function intentionally does not take
    care of key errors.
    '''
    secret = load_secret()
    max_results = secret["max_results"]
    options = get_quiet_options()
    logger.info("Searching song from youtube...")
    url = f"ytsearch{max_results}:{query}"
    results = YoutubeDL(options).extract_info(url, download=False, process=False)
    logger.info("Done.")
    songs = []
    for entry in results["entries"]:
        songs.append(Song.from_entry(entry))
    return songs


def search_songs(query: str) -> list[Song] | None:
    '''
    Description
    -----------
    General purpose function for searching songs from youtube.
    Returns None if url could not be parsed by ytdl.
    '''
    urltype = analyze_url(query)
    if urltype in (URLtype.YT_WATCH, URLtype.YT_PLAYLIST):
        return get_songs_from_youtube(query)
    elif urltype == URLtype.NOT_URL:
        return search_songs_from_youtube(query)
    return None


def download_song(song: Song) -> bool:
    secret = load_secret()
    # if song is None
    if Song is None:
        return False
    # if song duration is too big
    if song.duration > secret["max_song_duration"]:
        return False
    # if song is already downloaded
    elif os.path.isfile(song.path):
        logger.warning(f"Already downloaded: {song.path}")
        return True
    # download
    options = get_download_options()
    options.update(get_quiet_options())
    logger.info("Downloading song...")
    YoutubeDL(options).download(song.url)
    logger.info("Done.")
    return True


__all__ = ["clear_downloads", "search_songs", "download_song"]
