from discord.ext import commands
from discord.ext.commands import CommandError
from util.etc import gm_from_ctx

class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def stfu(self, ctx):
        """Prevents me from speaking unless spoken to"""
        gm = gm_from_ctx(ctx)
        gm.config['stfu'] = True
        await ctx.send('Okay :(')

    @commands.command()
    async def really_stfu(self, ctx):
        """Prevents me from speaking at all unless responding to a command"""
        gm = gm_from_ctx(ctx)
        gm.config['really_stfu'] = True
        await ctx.send('If you say so ;_;')

    @commands.command()
    async def wakeup(self, ctx):
        """Reverses a previous 'stfu' and allows me to speak again"""
        gm = gm_from_ctx(ctx)
        gm.config['stfu'] = False
        gm.config['really_stfu'] = False
        await ctx.send('Yay! :D')

    @commands.command()
    async def probability(self, ctx, arg: int):
        """Sets the probability of responding to a message (1-100)"""
        if arg < 1 or arg > 100:
            raise CommandError("Must be a number between 1 and 100")
        gm = gm_from_ctx(ctx)
        gm.config['speak_probability'] = int
        await ctx.send(f"Now replying {arg}% of the time.")

    @commands.command()
    async def save(self, ctx):
        """Save current brainfile to disk"""
        gm = gm_from_ctx(ctx)
        gm.reload_model()
        await ctx.send("Done.")

    @commands.command()
    async def dumpconfig(self, ctx):
        """Shows current configuration in this server"""
        gm = gm_from_ctx(ctx)
        await ctx.send(gm.config)

    @commands.command()
    async def reloadconfig(self, ctx):
        """Reloads the configuration from disk"""
        bot = gm_from_ctx(ctx).bot
        bot._reload_config()
        await ctx.send('Configuration reloaded from disk.')

   # @commands.command()
   # async def help(self, ctx):
   #     ctx.send("**!stfu**: Don't speak unless spoken to | **!really_stfu**: Don't speak at all. Use sparingly. | **!probability (1-100)**: Only reply this in 100 messages | **!wakeup**: Allow to speak again (negates stfu)")

