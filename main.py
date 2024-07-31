from utils.bot import *
from utils.logger import *
from utils.secret import *

logger = get_logger(__name__)


def main():
    secret = load_secret()
    # bot
    bot = VoiceBot()
    bot.run(secret["bot_token"])


if __name__ == "__main__":
    main()
