import markovify
import discord
import sys
import random
import yaml
import os
import atexit
import copy
import re
import uuid
import time

from util.chat import should_ignore_message, clean_text, GuildModel
from util.commands.chat import ChatCommands

class MariBot(discord.ext.commands.bot.Bot):
    config = None
    models = {}
    ready = False
    sentry = None

    def __init__(self, bot_config: dict=None):
        super().__init__(bot_config['system']['command_prefix'])
        self.config = bot_config
        self.add_cog(ChatCommands(self))
        # Sentry.io integration
        if 'sentry' in self.config.keys():
            import sentry_sdk
            self.sentry = sentry_sdk
            self.sentry.init(self.config['sentry']['init_url'], environment="production")
            print("*** Sentry.io integration enabled")


    def _reload_config(self):
        print(f"*** Reloading configuration by request")
        with open('config.yml', 'r') as file:
            self.config = yaml.safe_load(file)
        for model in self.models.keys():
            self.models[model].config = self.config['guilds'][model]

    def _init_guild(self, guild):
        """Persist a new guild to the configuration file"""
        print(f"*** Initializing new configuration for {guild.name}")
        defs = copy.deepcopy(self.config['guild_defaults'])
        self.config['guilds'][guild.name] = defs
        self.config['guilds'][guild.name]['brainfile'] = str(guild.id) + '.json'
        self._save_config()

    def _initialize_brains(self):
        """
        Loads brainfiles for all servers the bot is connected to.
        Should be called after bot is in the ready state so that
        client.guilds` is populated.
        """
        for guild in self.guilds:
            if guild.name not in self.config['guilds']:
                self._init_guild(guild)
               

            gm = GuildModel(
                self.config['guilds'][guild.name],
                guild.name
            )

            self.models[guild.name] = gm
            self.ready = True
    
    def _save_config(self):
        """Persist the bot configuration to disk"""
        with open('config.yml', 'w') as conffile:
            conffile.write(yaml.dump(self.config))

    def _format_message(self, message: discord.Message, prefix=None):
        """Return a string representation of a message with given prefix"""
        return f"[{prefix}] <{message.author.name}>: {message.content}"
  
    def learn(self, message: discord.Message):
        """Take the incoming message and combine it with the model, persisting a new model."""
        gm = self.models[message.guild.name]
        gm.counter += 1

        # Implicitly ignore anything with the current command prefix as well
        if self.config['system']['command_prefix'] in message.content[0]:
            print(self._format_message(message, "NOLEARN:COMMAND"))
            return

        for line in message.content.splitlines():
            newmod = markovify.Text(line, well_formed=False, retain_original=False)
            gm.model = markovify.combine([gm.model, newmod])
            print(self._format_message(message, "LEARN"))
        if gm.counter >= gm.config['save_every']:
            gm.counter = 0
            gm.reload_model()

    async def speak(self, message: discord.Message):
        """
        Reply to the provided message using a randomly generated sentence.
        If the model generates an empty sentence, send '...' instead.
        """
        gm = self.models[message.guild.name]
        sentence = gm.model.make_sentence(tries=10)
        if len(sentence) == 0:
            await message.channel.send("...")
        else:
            await message.channel.send(sentence)

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print('Loading brains..')
        self._initialize_brains()
        print('Ready.')

    async def on_message(self, message: discord.Message):
        await self.process_commands(message)
        gm = self.models[message.guild.name]
        
        if should_ignore_message(message, gm.config, self):
            return
        
        # Don't do anything unless models are ready
        if not self.ready:
            print(self._format_message(message, "NOSPEAK:NOTREADY"))
            return

        addressed = True if self.user.name.lower() in message.content.lower() else False
        message.content = clean_text(message.content, self)

        if gm.config['learn_enabled']:
            self.learn(message)
        if gm.config['really_stfu']:
            print(self._format_message(message, "NOSPEAK:RLYSTFU"))
            return
        if gm.config['stfu'] and not addressed:
            print(self._format_message(message, "NOSPEAK:STFU"))
            return
        if gm.config['ignore_bots'] and message.author.bot:
            print(self._format_message(message, "NOSPEAK:BOT"))
            return
        if not random.randint(1, 100) <= gm.config['speak_probability'] and not addressed:
            print(self._format_message(message, "NOSPEAK:PROBABILITY"))
            return
        else:
            await self.speak(message)
            

    async def on_guild_join(self, guild):
        """
        Hook for when the bot is added to a new guild.
        Presists a new configuration, copied from the default.
        """
        print(f"*** Joined {guild.name}")
        self._init_guild(guild)
        
        gm = GuildModel(
            self.config['guilds'][guild.name],
            guild.name
        )
        self.models[guild.name] = gm

    async def on_guild_remove(self, guild):
        print(f"Removed from {guild.name}")

    async def on_connect(self):
        print("*** Connected to Discord. Attempting to login..")

    async def on_disconnect(self):
        print("*** Lost connection to Discord.")
    
    async def on_resumed(self):
        print("*** Reconnected")
    
    async def on_error(self, event, *args, **kwargs):
        # Sentry.io integration
        if self.sentry:
            with self.sentry.configure_scope() as scope:
                scope.set_tag("bot_event", event)
                scope.set_extra("event_args", args)
                scope.set_extra("event_kwargs", kwargs)
                self.sentry.capture_exception(sys.exc_info())

    def shutdown(self):
        """Shutdown handler, forces all models to save."""
        for model in self.models.keys():
            self.models[model].save_model()
        self._save_config()
        print("*** Saving models and shutting down")


print("*** Bot startup..")
conf = None
with open('config.yml', 'r') as file:
    conf = yaml.safe_load(file)
    print("*** Configuration loaded")

bot = MariBot(bot_config=conf)
atexit.register(bot.shutdown)
bot.run(conf['system']['bot_token'])
