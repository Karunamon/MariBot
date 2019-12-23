MariBot
=======

![Python version](https://img.shields.io/github/pipenv/locked/python-version/Karunamon/MariBot) ![License](https://img.shields.io/github/license/Karunamon/MariBot) ![Dependencies](https://img.shields.io/librariesio/github/Karunamon/MariBot)

A simple Markov Chatterbot for Discord

Maribot is based on the [Markovify](https://github.com/jsvine/markovify) and [Discord.py](https://github.com/Rapptz/discord.py) libraries. In short, it learns from the chat about how sentences are usually formed, and then every so often, randomly injects something based on what it learned. The results are random, and often, hilarious.

Installation
------------

* Clone this repository
* Install requirements. Ensure that [pipenv](https://pypi.org/project/pipenv/) is available, and execute `pipenv install`
* Copy `config.yml.example` to `config.yml`
  * Do not remove the `test_guild_please_ignore` line.
  * Change config.yml defaults as you wish.
* [Register a new Discord bot](https://discordpy.readthedocs.io/en/latest/discord.html)
  * When you arrive at the bot permissions page, check the "view channels" and "send messages" permissions.
  * Copy the token and place it in the `bot_token` section `config.yml`
* On a server you have administrator rights on, use the constructed URL from the Discord bot dashboard and invite it into the server.

Usage
-----

Simply speak as normal. MariBot will not do very much until she has had some time to listen to conversations on your server. By default, MariBot is set to `!stfu`, meaning that she will not speak unless addressed by name. It is recommended that you leave this setting alone until some time has passed (a few days, at least, less on busy servers). The more chat she sees, the better the results.

Once you feel that enough time has passed, use `!wakeup`, and set the `!probability` to something low, like 5. (5% is a 1/20 chance of responding.) Anything much higher is likely to annoy people in the chat :)

Use `!help` for commands.

Note that ***no permission checking is done*** - this is because chatterbots like MariBot tend to be contentious (and occasionally offensive), and it is important that people are able to silence the bot when they feel annoyed by it.
