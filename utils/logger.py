import logging

from logging import Logger

from utils.secret import *

from discord.utils import _ColourFormatter, stream_supports_colour


def get_logger(name: str) -> Logger:
    '''
    Returns
    -------
    Returns a logger with the given name.
    '''
    secret = load_secret()
    logger = logging.getLogger(name)
    # logger level
    if secret["mode"] == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif secret["mode"] == "RELEASE":
        logger.setLevel(logging.WARNING)
    # logger stream
    stream = logging.StreamHandler()
    if stream_supports_colour(stream.stream):
        formatter = _ColourFormatter()
    else:
        dt_fmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style='{')
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    return logger


__all__ = ["get_logger"]
