import discord
import re
import markovify

class GuildModel(object):
    """Container struct for associated guilds (servers) with their data"""
    model = None
    config = None
    guild = None
    brainfilename = None
    counter = 0
    timers = {}

    def __init__(self, config: dict, guild: str):
        self.config = config
        self.guild = guild
        self.brainfilename = config['brainfile']
        self.last_enabler = None
        self.last_disabler = None
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

    # def add_timer(self, seconds: int, starttime: int, kind: str):
    #     self.timers[uuid.uuid1()] = {start: starttime, seconds: seconds, kind: kind}
    #     print(f"[NEWTIMER]: {seconds} seconds, {description} ({kind})")
    
    # def check_timers(self):
    #     for timer in self.timers:
    #         if timer['starttime'] + timer['seconds'] >= time.time():
    #             return timer
    #             del(self.timers[timer])
    

def should_ignore_message(message: discord.Message, gmconfig: dict, bot: discord.Client) -> bool:
    """
    Determines whether the passed message should be ignored (i.e.
    not learned or replied to) based on the attributes of the message
    and the configuration of the server
    """
    if message.channel.name in gmconfig['ignored_channels']:
        return True
    elif message.author.id in gmconfig['ignored_users']:
        return True
    elif message.author == bot.user:
        return True
    
    return False

    
def clean_text(message_text: str, bot: discord.Client) -> str:
    """Runs various cleanup processes on incoming messages, returning the cleaned text"""
    text = message_text
    # Convert UserIDs to textual names to avoid triggering mentions
    mention_matches = re.search(r'(?:.+)?(<@!?\d+>)(?:.+)?', text)
    if mention_matches:         
        for mention in mention_matches.groups():
            # looks like <@421925019447328769>
            uid_n = int(''.join(i for i in mention if i not in '<>@!'))
            try:
                # This can occasionally fail due to Discord shenanigans
                username = bot.get_user(uid_n).display_name
                print(f"[MENTION->USERNAME] {mention} -> {username}")
            except (TypeError, NameError, AttributeError) as e:
                print(f"[ERROR: MENTION->USERNAME]: {text} >> {e}")
                return ""  # Just send an empty string back, which will abort learning
            text = re.sub(mention, username, text)

    # Let's not get obsessed with our own name
    text = re.sub(bot.user.name, '', text, flags=re.IGNORECASE).strip()

    # Strip extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text