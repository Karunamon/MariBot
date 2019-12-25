import discord
import re

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