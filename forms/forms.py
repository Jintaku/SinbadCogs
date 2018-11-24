import discord
from redbot.core import commands, checks
from redbot.core.config import Config
from redbot.core.i18n import Translator, cog_i18n


_T = Translator("This is pointless", __file__)
_ = lambda s: s
# Strings go here


# ## Strings below no longer guarded.


class Forms(commands.Cog):
    """
    WIP
    """

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=78631113035100160, force_registration=True)

    