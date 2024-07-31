import cli
import importlib

from discord.ext import commands

from utils import messages
from utils.bot import *
from utils.player import *
from utils.secret import *


class Developer(commands.Cog):
    def __init__(self, bot: VoiceBot):
        self.bot = bot

    @staticmethod
    async def check_developer(ctx: commands.Context) -> bool:
        secret = load_secret()
        is_developer = str(ctx.author.id) in secret["developers"]
        if not is_developer:
            await ctx.reply(messages.dev_only_command)
            return False
        return True

    @commands.command(
        name="shutdown",
        description="Yui shuts down."
    )
    async def shutdown(self, ctx: commands.Context):
        '''
        Description
        -----------
        Simply shuts down, but if she is in a voice channel she
        plays a shutdown tune before leaving and shutting down.
        '''
        if not (await Developer.check_developer(ctx)):
            return
        self.bot.context = ctx
        await self.bot.close()

    @commands.command(
        name="execute",
        description="Executes the CLI routine."
    )
    async def execute(self, ctx: commands.Context, *args):
        if not (await Developer.check_developer(ctx)):
            return
        importlib.reload(cli)
        await cli.routine(ctx, *args)


async def setup(bot: VoiceBot):
    await bot.add_cog(Developer(bot))
