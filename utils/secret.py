import json

from typing import TypedDict, Literal, Any

secret_file = "secret.json"


class secret_t(TypedDict):
    bot_prefix: str
    application_id: str
    bot_token: str
    permissions: str
    scopes: list[str]
    custom_activity: dict[Literal["activity", "emoji"], str]
    cogs: list[str]
    mode: Literal["RELEASE", "DEBUG"]
    developers: list[str]
    ffmpeg_options: dict[Literal["before_options", "options"], str]
    quality: str
    extension: str
    download_path: str
    max_song_duration: int
    max_download_size: int
    max_results: int


def load_secret() -> secret_t:
    '''
    Description
    -----------
    Loads `secret.json` file and returns a dictionary
    corresponding to the JSON data.
    '''
    with open(secret_file, 'r', encoding='utf-8') as fp:
        return json.load(fp)


def save_secret(secret: secret_t):
    '''
    Description
    -----------
    Saves `secret` into `secret.json` in JSON format.
    '''
    with open(secret_file, 'w', encoding='utf-8') as fp:
        json.dump(secret, fp, ensure_ascii=False, indent='\t')


__all__ = ["load_secret", "save_secret", "secret_t"]
