# MariBot: A simple Markov Chatterbot for Discord

Maribot is based on the [Markovify](https://github.com/jsvine/markovify) library. In short, it learns from the chat about how sentences are usually formed, and then every so often, randomly injects something based on that chat. The results are random, and often, hilarious.


# Installation

* Clone this repository
* Install requirements: `install -r requirements.txt`
* Copy `config.yml.example` to `config.yml`
  * Do not remove the `test_guild_please_ignore` line.
  * Change config.yml defaults as you wish.
* [Register a new Discord bot](https://discordpy.readthedocs.io/en/latest/discord.html)
  * When you arrive at the bot permissions page, check the "view channels" and "send messages" permissions.
  * Copy the token and place it in the `bot_token` section `config.yml`
* On a server you have administrator rights on, use the constructed URL from the Discord bot dashboard and invite it into the server.


# Usage

Simply speak as normal. MariBot will not do very much until she has had some time to listen to conversations on your server. It is recommended that you set her to `!stfu` until some time has passed (a few days, at least, less on busy servers).

Once you feel that enough time has passed, use `!wakeup`, and set the `!probability` to something low, like 5. (5% is a 1/20 chance of responding.)

Use `!help` for commands.


Note that ***no permission checking is done*** - this is because chatterbots like MariBot tend to be contentious (and occasionally offensive), and it is important that people are able to silence the bot when they feel annoyed by it.