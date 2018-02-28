import discord
import pathlib
from cogs.utils.dataIO import dataIO
from discord.ext import commands
from cogs.utils import checks

path = 'data/advstatus'


class AdvStatus:
    """
    Quick and dirty cog for allowing the playing/watching/or listening statuses
    """

    __version__ = "1.0.0"
    __author__ = "mikeshardmind (Sinbad#0001)"

    status_dict = {
        'playing': 0,
        'listening': 2,
        'listenging': 2,  # 13d4809d1979c9c093b12d7e79d4ccaed8ada215
        'watching': 3
    }

    def __init__(self, bot):
        self.bot = bot
        try:
            self.settings = dataIO.load_json(path + '/settings.json')
        except Exception:
            self.settings = None
        else:
            self.bot.loop.create_task(
                self.modify_presence(
                    self.settings['type'], self.settings['title']
                                  ))

    def save_settings(self):
        dataIO.save_json(path + '/settings.json', self.settings)

    @checks.is_owner()
    @commands.command(
        name='changepresence', pass_context=True, aliases=['advstatus'])
    async def changepresence(self, ctx, gametype, *, gamename):
        """
        gametype should be playing, listening, or watching

        or a numeric value based on the below
        'playing'   : 0,
        'listening' : 2,
        'watching' : 3

        To set streaming look at [p]help set stream
        """

        if len(gamename.strip()) == 0:
            return await self.bot.say('cant set an empty status')
        else:
            title = gamename.strip()

        try:
            gt = int(gametype)
        except ValueError:
            gt = self.status_dict.get(gametype.strip().lower(), -1)

        if gt not in self.status_dict.values():
            return await self.bot.send_cmd_help(ctx)

        await self.modify_presence(gt, title)
        self.settings = {'type': gt, 'title': title}
        self.save_settings()
        await self.bot.say("Done.")

    async def modify_presence(self, gt: int, title: str):
        current_status = list(self.bot.servers)[0].me.status
        game = discord.Game(name=title, type=gt)
        await self.bot.change_presence(game=game, status=current_status)


def setup(bot):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    bot.add_cog(AdvStatus(bot))
