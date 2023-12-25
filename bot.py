import interactions
from os import getenv
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("TOKEN")
NERD_USER = int(getenv("NERD_USER"))

bot = interactions.Client(intents=interactions.Intents.DEFAULT | interactions.Intents.MESSAGE_CONTENT)

# boilerplate for commands

# @interactions.slash_command(name="command", description="kekw")
#async def _(ctx: interactions.SlashContext):

#    await ctx.send(response)

@interactions.listen()
async def on_message_create(event: interactions.api.events.MessageCreate):
    if event.message.author == bot.user:
        return
    
    # message nerder
    if event.message.author.id == NERD_USER:
        await event.message.add_reaction("\U0001F913")

    # pretty self explanatory
    if "nigg" in event.message.content:
        await event.message.channel.send(":warning:")

@interactions.listen()
async def on_startup():
    print("Bot ready")

bot.start(TOKEN)