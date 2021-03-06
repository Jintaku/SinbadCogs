from redbot.core import commands


def tmpc_active():
    async def check(ctx: commands.Context):
        if not ctx.guild:
            return False
        cog = ctx.bot.get_cog("RoomTools")
        if not cog:
            return False
        return await cog.tmpc_config.guild(ctx.guild).active()

    return commands.check(check)


def aa_active():
    async def check(ctx: commands.Context):
        if not ctx.guild:
            return False
        cog = ctx.bot.get_cog("RoomTools")
        if not cog:
            return False
        return await cog.ar_config.guild(ctx.guild).active()

    return commands.check(check)
