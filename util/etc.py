import discord
from util.chat import GuildModel

def gm_from_ctx(ctx: discord.ext.commands.Context) -> GuildModel:
    """
    Retrives the appropriate GuildModel object based on the provided
    Context. GuildModel is used to store per-channel configuration,
    and since discord.ext.commands is separated from the normal
    bot initialization, we have to do some kind of mobius double
    reach-around to get the right model back out.

    gm_from_ctx -> Context -> Bot -> models -> individual GM
    """
    return ctx.bot.models[ctx.guild.name]