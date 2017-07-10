import discord
from .utils import checks
from discord.ext import commands
from cogs.utils.dataIO import dataIO
import os
from datetime import datetime as dt
import random


class ChannelDraw:
    """Draws a random message from a set"""

    __author__ = "mikeshardmind"
    __version__ = "2.0"

    def __init__(self, bot):
        self.bot = bot
        self.users = []
        self.locks = []
        self.settings = dataIO.load_json('data/channeldraw/settings.json')

    def save_json(self):
        dataIO.save_json("data/channeldraw/settings.json", self.settings)

    @checks.admin_or_permissions(Manage_channels=True)
    @commands.group(pass_context=True, name='draw', no_pm=True)
    async def draw(self, ctx):
        """Need I say more?"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @draw.command(pass_context=True, name='bymessageids', aliases=["bmids"])
    async def by_msgs(self, ctx, first: str, last: str):
        if self.is_user_shamed(ctx.message.author):
            return await("I'm Not letting you waste my time right now.")
        if ctx.message.author.id in self.users:
            return await self.bot.say("You already have a drawing in progress")
        a = await self.get_msg(first)
        b = await self.get_msg(last)
        if a is None or b is None:
            return await self.bot.say("I could not find one or both of those")
        if a.channel.id != b.channel.id:
            return await self.bot.say("Those messages are in seperate rooms")
        if a.channel.id in self.locks:
            return await self.bot.say("That channel has a drawing in progress")
        if a.timestamp >= b.timestamp:
            a, b = b, a  # Because I can't trust people to use things correctly

        msgs = await self.mkqueue(a.timestamp, b.timestamp, b.channel)
        msgs.append(a)
        msgs.append(b)
        await self.validate(msgs, ctx.message.author)

    @draw.command(pass_context=True, name='bytimes')
    async def by_times(self, ctx, *, times):
        """gets messages from the channel it was called from between 2 times.\n
        Format should be \nYYYY-MM-DDHH:mm\n
        In chronological order, with a space inbetween them"""
        if self.is_user_shamed(ctx.message.author):
            return await("I'm Not letting you waste my time right now.")
        try:
            t = str(times)
            start, end = t.split(' ')
            start = ''.join(c for c in start if c.isdigit())
            end = ''.join(c for c in end if c.isdigit())
            a = dt.strptime(start, "%Y%m%d%H%M")
            b = dt.strptime(end, "%Y%m%d%H%M")
        except ValueError:
            return await self.bot.send_cmd_help(ctx)
        if a >= b:
            a, b = b, a
        if b > ctx.message.timestamp:
            b = ctx.message.timestamp
        if a >= ctx.message.timestamp:
            return await self.bot.say("I can't read the future.")
        if ctx.channel.id in self.locks:
            return await self.bot.say("That channel has a drawing in progress")
        if ctx.message.author.id in self.users:
            return await self.bot.say("You already have a drawing in progress")

        msgs = await self.mkqueue(a, b, ctx.message.channel)
        await self.validate(msgs, ctx.message.author)

    @draw.command(pass_context=True, name='fromdate')
    async def by_interval(self, ctx, *, time):
        """gets messages from the channel it was called from
        between now and a time (UTC).\n
        Format should be \n\`YYYY-MM-DDHH:mm\`\n
        """
        if self.is_user_shamed(ctx.message.author):
            return await("I'm Not letting you waste my time right now.")
        try:
            t = str(time)
            t = ''.join(c for c in t if c.isdigit())
            a = dt.strptime(t, "%Y%m%d%H%M")
            b = dt.utcnow
            pass
        except ValueError:
            return await self.bot.send_cmd_help(ctx)
        if a >= b:
            return await self.bot.send_cmd_help(ctx)
        if ctx.message.author.id in self.users:
            return await self.bot.say("You already have a drawing in progress")
        if ctx.message.channel.id in self.locks:
            return await self.bot.say("That channel has a drawing in progress")

        msgs = await self.mkqueue(a, b, ctx.message.channel)
        await self.validate(msgs, ctx.message.author)

    @draw.command(name="auto", pass_context=True)
    async def autodraw(self, ctx):
        """only works if there is a prior draw on record"""
        if self.is_user_shamed(ctx.message.author):
            return await("I'm Not letting you waste my time right now.")
        if not self.settings['latest'][ctx.message.channel.id]:
            return await self.bot.send_cmd_help(ctx)
        if ctx.message.author.id in self.users:
            return await self.bot.say("You already have a drawing in progress")
        if ctx.message.channel.id in self.locks:
            return await self.bot.say("That channel has a drawing in progress")

        a = dt.strptime(self.settings['latest'][ctx.message.channel.id],
                        "%Y%m%d%H%M")
        b = ctx.message.timestamp
        msgs = await self.mkqueue(a, b, ctx.message.channel)
        await self.validate(msgs, ctx.message.author)

        self.settings['latest'][ctx.channel.id] = \
            ctx.message.timestamp.strftime("%Y%m%d%H%M")
        self.save_json()

    async def validate(self, msgs=[], author=None):
        temp_latest = msgs[-1].timestamp
        channel = msgs[0].channel
        fail_count = 0
        random.seed()
        random.shuffle(msgs)

        while author.id in self.locks:
            if fail_count == 1:
                await self.bot.send_message(author, "Quit wasting my time.")
            if fail_count == 2:
                await self.bot.send_message(author, "Next one either quit "
                                            "or do it correctly")
            if fail_count == 3:
                await self.shame(channel, author)
                break
            if len(msgs) == 0:
                await self.bot.send_message(author, "That's all folks")
                break
            dm = await self.bot.send_message(author,
                                             "Is the following a valid entry?"
                                             "(yes/no/quit)")
            entry = self.queue.pop()
            em = self.qform(entry)
            await self.bot.send_message(author, embed=em)
            timeout = None if self.bot.settings.owner.id == author.id \
                else 60
            message = await self.bot.wait_for_message(
                                                channel=dm.channel,
                                                author=author, timeout=timeout)
            if message is None:
                fail_count += 1
                continue
            reply = message.clean_content.lower()

            if reply[0] == 'y':
                await self.bot.send_message(channel,
                                            "{} won the drawing with "
                                            "the following entry"
                                            "".format(entry.author.mention))
                await self.bot.send_message(channel, embed=em)
                self.settings['latest'][channel.id] = \
                    temp_latest.strftime("%Y%m%d%H%M")
                self.save_json()
            if reply[0] == 'n':
                await self.bot.send_message(self.user, "Ok then...")
            if reply[0] == 'q':
                await self.bot.send_message(self.user,
                                            "I guess we're done here")
                break
        self.users.remove(author)
        self.locks.remove(channel)

    async def shame(self, channel, user):

        self.bot.send_message(channel, "{} is incapable of answering a prompt "
                              "of 'yes/no/quit?' and will be unable to use "
                              "the draw for 1 week."
                              "".format(user.mention))
        self.settings['shame']['user.id'] = dt.utcnow().strftime("%Y%m%d%H%M")
        self.save_json()

    def is_user_shamed(self, user):
        if user.id not in self.settings:
            return False
        t = dt.strptime(self.settings['shame']['user.id'], "%Y%m%d%H%M") \
            + dt.timedelta(weeks=1)
        return True if t > dt.utcnow() else False

    async def mkqueue(self, a, b, channel):
        queue = []
        async for message in \
                self.bot.logs_from(channel, limit=1000000,
                                   after=a, before=b, reverse=True):
                queue.append(message)

    async def get_msg(self, message_id: str, server=None):
        if server is not None:
            for channel in server.channels:
                try:
                    msg = await self.bot.get_message(channel, message_id)
                    if msg:
                        return msg
                except Exception:
                    pass
            return None

        for server in self.bot.servers:
            for channel in server.channels:
                try:
                    msg = await self.bot.get_message(channel,  message_id)
                    if msg:
                        return msg
                except Exception:
                    pass

    def qform(self, message):
        channel = message.channel
        server = channel.server
        content = message.clean_content
        author = message.author
        sname = server.name
        cname = channel.name
        timestamp = message.timestamp.strftime('%Y-%m-%d %H:%M')
        avatar = author.avatar_url if author.avatar \
            else author.default_avatar_url
        if message.attachments:
            a = message.attachments[0]
            fname = a['filename']
            url = a['url']
            content += "\nUploaded: [{}]({})".format(fname, url)
        footer = 'Said in {} #{} at {} UTC'.format(sname, cname, timestamp)
        em = discord.Embed(description=content, color=discord.Color.purple())
        em.set_author(name='{}'.format(author.name), icon_url=avatar)
        em.set_footer(text=footer)
        return em


def check_folder():
    f = 'data/channeldraw'
    if not os.path.exists(f):
        os.makedirs(f)


def check_file():
    f = 'data/channeldraw/settings.json'
    if dataIO.is_valid_json(f) is False:
        dataIO.save_json(f, {'latest': {}, 'shame': {}})


def setup(bot):
    check_folder()
    check_file()
    n = ChannelDraw(bot)
    bot.add_cog(n)
