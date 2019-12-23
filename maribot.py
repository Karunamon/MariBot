import markovify
import discord
import sys
import random
import yaml
import os
import atexit
import copy
import re


class GuildModel(object):
    """Container struct for associated guilds (servers) with their data"""
    model = None
    config = None
    guild = None
    brainfilename = None
    counter = 0

    def __init__(self, config: dict, guild: str):
        self.config = config
        self.guild = guild
        self.brainfilename = config['brainfile']
        try:
            with open(self.brainfilename) as file:
                print(f"Attempting to load brainfile for {self.guild}...")
                self.model = markovify.Text.from_json(file.read())
                print(f"Loaded {self.brainfilename} successfully")
        except IOError:
            print(f"Creating new brainfile for {guild}")
            self.model = markovify.Text('y helo thar', well_formed=False)
            self.save_model()

    def reload_model(self):
        self.save_model()
        self.load_model()

    def save_model(self):
        j = self.model.to_json()
        with open(self.brainfilename, 'w') as file:
            file.write(j)

    def load_model(self):
        with open(self.brainfilename, 'r') as file:
            self.model = markovify.Text.from_json(file.read())


class MariBot(discord.Client):
    config = None
    models = {}
    ready = False

    def __init__(self, config: dict):
        super().__init__()
        self.config = config

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

    def _format_message(self, message, prefix=None):
        """Return a string representation of a message with given prefix"""
        return f"[{prefix}] <{message.author.name}>: {message.content}"

    async def command(self, message: discord.Message):
        sentence = message.content.split(' ')
        command = sentence[0].lower()
        gm = self.models[message.guild.name]
        if command == '!stfu':
            gm.config['stfu'] = True
            await message.channel.send('Okay :(')
            return
        elif command == '!really_stfu':
            gm.config['really_stfu'] = True
            await message.channel.send('If you say so..')
            return
        elif command == '!wakeup':
            gm.config['stfu'] = False
            gm.config['really_stfu'] = False
            await message.channel.send('Yay! :D')
            return
        elif command == '!probability':
            try:
                newprob = int(sentence[1])
                if newprob < 1 or newprob > 100:
                    raise RuntimeError("Probability must be a number between 1 and 100")
            except Exception as e:
                await message.channel.send(repr(e))
                return
            gm.config['speak_probability'] = newprob
            await message.channel.send(f"Now replying {newprob}% of the time")
            return
        elif command == '!save':
            gm.reload_model()
            await message.channel.send(f"Done!")
        elif command == '!dumpconfig':
            await message.channel.send(gm.config)
        elif command == '!reloadconfig':
            self._reload_config()
            await message.channel.send('Reloaded global bot config')
        elif command == '!help':
            await message.channel.send("!stfu: Don't speak unless spoken to | !really_stfu: Don't speak at all | !probability (number): Only reply this often | !wakeup: Allow to speak")


    def learn(self, message: discord.Message):
        """Take the incoming message and combine it with the model, persisting a new model."""
        gm = self.models[message.guild.name]
        gm.counter += 1
        sentence = message.content.split(' ')
        
        # Naked file uploads, some rich messages, etc have no text content
        if not len(message.content) > 0:
            print(self._format_message(message, "NOLEARN:NOCONTENT"))
            return

        # Check for banned words
        if len([w for w in sentence if w in gm.config['banned_words']]) > 0:
            print(self._format_message(message, "NOLEARN:BANNEDWORD"))
            return

        # Check for banned regexes
        for rex in gm.config['banned_regexes']:
            if re.match(rex, message.content):
                print(self._format_message(message, "NOLEARN:BANNEDREX"))
                return

        #Let's not get obsessed with our own name
        sentence = [x for x in sentence if self.user.name in x]

        newmod = markovify.Text(message.content, well_formed=False, retain_original=False)
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

    async def on_message(self, message):
        gm = self.models[message.guild.name]

        # Don't do anything unless models are ready
        if not self.ready:
            print(self._format_message(message, "NOSPEAK:NOTREADY"))
            return

        # Don't trigger on our own messages
        if message.author == self.user:
            return

        if message.content.startswith('!'):
            await self.command(message)

        else:
            addressed = True if self.user.name in message.content else False
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
        print("*** Lost connection to Discord. Exiting.")
        sys.exit(1)
    
    def shutdown(self):
        """Shutdown handler, forces all models to save."""
        for model in self.models.keys():
            self.models[model].save_model()
        print("*** Saving models and shutting down")


print("*** Bot startup..")
conf = None
with open('config.yml', 'r') as file:
    conf = yaml.safe_load(file)
    print("*** Configuration loaded")
bot = MariBot(conf)

atexit.register(bot.shutdown)
bot.run(conf['system']['bot_token'])
