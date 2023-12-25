# bot.py
import random

from discord.ext import commands
from discord import Intents

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.command(name='99')
async def _(ctx):
    if ctx.author == bot.user:
        return

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.channel.send(response)

bot.run("MTE4ODYyNTAxMTY3NDcyNjQwMA.GBKHLC.2NsxWC17DJ4s3CUzkm9esN4P_nOpaEZCpRugWw")