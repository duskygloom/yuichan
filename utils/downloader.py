import os

from yt_dlp import YoutubeDL
# from functools import partial
# from discord.ext import commands

from utils.song import *
from utils.logger import *
from utils.secret import *

secret = load_secret()
logger = get_logger(__name__)

ytdl_options = {
    "format": f"{secret['extension']}/{secret['quality']}",
    "outtmpl": f"{secret['download_path']}/%(id)s.{secret['extension']}",
    "noplaylist": True
}


def clear_downloads():
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


# async def get_songs(ctx: commands.Context, query: str) -> list[Song]:
#     search_function = partial(search, query)
#     await ctx.message.add_reaction('⏳')
#     search_results: list[Song] = await ctx.bot.loop.run_in_executor(None, search_function)
#     await ctx.message.remove_reaction('⏳', ctx.bot.user)
#     return search_results


# async def download_song(ctx: commands.Context, song: Song) -> bool:
#     await ctx.message.add_reaction('⬇️')
#     status = download(song)
#     await ctx.message.remove_reaction('⬇️', ctx.bot.user)
#     return status


def search_songs(query: str) -> list[Song]:
    max_results = secret["max_results"]
    results = []
    try:
        # assuming query is a youtube link
        info = YoutubeDL().extract_info(
            url=query, 
            download=False,
            process=False
        )
        if info.get("webpage_url_basename") == "playlist":
            for entry in info.get("entries"):
                results.append(Song.from_info(entry))
        else:
            results.append(Song.from_info(info, True))
    except Exception as e:
        logger.warning(e)
        # error means the youtube link was not found
        matches = YoutubeDL().extract_info(
            url=f"ytsearch{max_results}:{query}", 
            download=False, 
            process=False
        )
        for match in matches.get("entries"):
            try:
                results.append(Song.from_info(match))
            except TypeError as e:
                logger.error(e)
    return results


def download_song(song: Song) -> bool:
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
    YoutubeDL(ytdl_options).download(song.url)
    return True


__all__ = ["clear_downloads", "search_songs", "download_song"]
