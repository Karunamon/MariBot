from discord.ext import commands
from discord.ext.commands import CommandError
from util.etc import gm_from_ctx

def format_mode(config: dict) -> str:
    if config["really_stfu"]:
        return "Really STFU (silent except for commands)"
    elif config["stfu"]:
        return "STFU (silent unless mentioned by name)"
    else:
        return "Normal (speaks according to probability)"

def format_config(model) -> str:
    """Formats a GuildModel configuration for pretty output"""
    config = model.config
    banned_regexes = ''
    ignored_users = ''
    ignored_channels = ''
    banned_words = ''
    if model.config['banned_regexes']:
        for i in model.config['banned_regexes']:
            banned_regexes += "\n  * " + i.replace("`", ":bt:")
    else:
        banned_regexes = "None"

    if model.config['ignored_users']:
        for i in model.config['ignored_users']:
            ignored_users += "\n  * " + i.replace("`", ":bt:")
    else:
        ignored_users = "None"
    
    if model.config['ignored_channels']:
        for i in model.config['ignored_channels']:
            ignored_channels += "\n  * " + i.replace("`", ":bt:")
    else:
        ignored_channels = "None"


    if model.config['banned_words']:
        for i in model.config['banned_words']:
            banned_words += "\n  * " + i.replace("`", ":bt:")
    else:
        banned_words = "None"
    

    return f"""```markdown
# Configuration for {model.guild}

* This server's brainfile: {config['brainfile']}
* Save brainfile to disk every: {config['save_every']} messages
* Learning enabled: {config['learn_enabled']}
* Speak mode: {format_mode(config)}
* Speak probability: %{config['speak_probability']}

* Ignored regexes: {banned_regexes}
* Ignored whole words: {banned_words}
* Ignored channels: {ignored_channels}
* Ignored users: {ignored_users}
* Ignore bots: {config['ignore_bots']}```"""
class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def stfu(self, ctx):
        """Prevents me from speaking unless spoken to"""
        gm = gm_from_ctx(ctx)
        gm.config['stfu'] = True
        gm.last_disabler = ctx.message.author.nick
        enablewords = f" (last enabled by {gm.last_enabler})" if gm.last_enabler else ""
        await ctx.send('Okay :(' + enablewords)

    @commands.command()
    async def really_stfu(self, ctx):
        """Prevents me from speaking at all unless responding to a command"""
        gm = gm_from_ctx(ctx)
        gm.config['really_stfu'] = True
        gm.last_disabler = ctx.message.author.nick
        enablewords = f" (last enabled by {gm.last_enabler})" if gm.last_enabler else ""
        await ctx.send('If you say so ;_;' + enablewords)

    @commands.command()
    async def wakeup(self, ctx):
        """Reverses a previous 'stfu' and allows me to speak again"""
        gm = gm_from_ctx(ctx)
        gm.config['stfu'] = False
        gm.config['really_stfu'] = False
        gm.last_enabler = ctx.message.author.nick
        disablewords = f" (last disabled by {gm.last_disabler})" if gm.last_disabler else ""
        await ctx.send('Yay! :D' + disablewords)

    @commands.command()
    async def probability(self, ctx, arg: int):
        """Sets the probability of responding to a message (1-100)"""
        if arg < 1 or arg > 100:
            raise CommandError("Must be a number between 1 and 100")
        gm = gm_from_ctx(ctx)
        gm.config['speak_probability'] = arg
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
        await ctx.send(format_config(gm))

    @commands.command()
    async def reloadconfig(self, ctx):
        """Reloads the configuration from disk"""
        bot = gm_from_ctx(ctx).bot
        bot._reload_config()
        await ctx.send('Configuration reloaded from disk.')

   # @commands.command()
   # async def help(self, ctx):
   #     ctx.send("**!stfu**: Don't speak unless spoken to | **!really_stfu**: Don't speak at all. Use sparingly. | **!probability (1-100)**: Only reply this in 100 messages | **!wakeup**: Allow to speak again (negates stfu)")

