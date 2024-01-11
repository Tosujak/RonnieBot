from os import getenv
from signal import SIGINT, SIGTERM
from asyncio import gather, get_event_loop, create_task, ensure_future
from time import sleep
from re import search
from dotenv import load_dotenv
from random import randint, choice
from datetime import datetime, timedelta
from interactions import (Client, Intents, Status, SlashContext, Member, Task, IntervalTrigger, TimeTrigger, OptionType, Activity, ActivityType, 
                          listen, slash_command, slash_option)
from interactions.api.events import MessageCreate

# Custom lib
from user import User, get_user, print_stats, print_gasparko_tierlist

load_dotenv()

TOKEN = getenv("TOKEN")
NERD_USER = int(getenv("NERD_USER"))
BAN_ROLE = int(getenv("BAN_ROLE"))
NORMAL_ROLE = int(getenv("NORMAL_ROLE"))
HLASKA_ROLE = int(getenv("HLASKA_ROLE"))
VAZENIE_ROOM = int(getenv("VAZENIE_ROOM"))
BOT_ROOM = int(getenv("BOT_ROOM"))
BAN_LIST = [] # list to keep track of votes
BANNED = [] # list of actually banned users
GASPARKO_LIST = []

BOT = Client(intents=Intents.DEFAULT | 
                          Intents.MESSAGE_CONTENT | 
                          Intents.GUILD_MEMBERS | 
                          Intents.GUILD_PRESENCES)

CP_OPTS = ["club penguin",
           "cheese pizza",
           "child porn",
           "competitive programming",
           "compromising positions",
           "copy paste",
           "cooked pasta",
           "cunt punt",
           "cell phone",
           "college program",
           "crazy pickles",
           "capture point",
           "cock piercing",
           "cibulova polievka",
           "cunt piercing",
           "cestovny poriadok",
           "cerebral palsy"]

GOOD_NWORDS = ["niggard",
               "niggerf",
               "nigger-f",
               "niggl",
               "snigger"]

# AUX METHODS #
################################################################
async def ban(bannee: User, ctx: SlashContext, str_format: str):
    bannee.set_duration(datetime.now() + timedelta(hours=bannee.get_duration()))
    BAN_LIST.pop(BAN_LIST.index(bannee))
    BANNED.append(bannee)
    message = str_format.format(**{"user": bannee.instance.display_name, "date": bannee.end_date})
    await ctx.guild.get_channel(VAZENIE_ROOM).send(message)
    await ctx.guild.get_channel(ctx.channel_id).send(message)
    sleep(1)
    await bannee.instance.add_role(BAN_ROLE)
    await bannee.instance.remove_role(NORMAL_ROLE)
    await bannee.instance.remove_role(HLASKA_ROLE)

async def admin_checker(ctx: SlashContext):
    if get_user(ctx.member.id, BANNED) and ctx.guild.is_owner(ctx.member.id):
        await ctx.send(f'{ctx.member.display_name} stop it, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return True
    else:
        return False

async def sig_handler(_):
    await BOT.get_channel(BOT_ROOM).send(f'{BOT.user.mention} **GOING OFFLINE**, smell ya later nerds <:nrd:1165680185933312120>')
    await gather(ensure_future(BOT.stop()))
    get_event_loop().stop()
################################################################

# TASKS #
#########################################
@Task.create(IntervalTrigger(seconds=30))
async def check_unban():
    unbanned = []
    for bannee in BANNED:
        if bannee.end_date < datetime.now():
            await bannee.instance.remove_role(BAN_ROLE)
            await bannee.instance.add_role(NORMAL_ROLE)
            await bannee.instance.add_role(HLASKA_ROLE)
            unbanned.append(BANNED.index(bannee))
    for i in unbanned:
        BANNED.pop(i)

@Task.create(TimeTrigger(hour=0, minute=0, utc=False))
async def reset():
    GASPARKO_LIST.clear()
#########################################

# ADMIN COMMANDS #
##########################################################################################
@slash_command(name="online", description="**ADMIN**: Get information about online users")
async def online(ctx: SlashContext):
    await ctx.guild.gateway_chunk()
    reply = ""
    for member in ctx.guild.humans:
        reply += f'{member.display_name} => {member.status}\n'
    reply += f'Total: {len([m for m in ctx.guild.humans if m.status and m.status != Status.OFFLINE])}'
    await ctx.send(reply, ephemeral=True)

@slash_command(name="list_permissions", description="**ADMIN**: List permissions for each of user's roles")
@slash_option(name="user", description="User to check", required=True, opt_type=OptionType.USER)
async def list_permissions(ctx: SlashContext, user: Member):
    await ctx.guild.gateway_chunk()
    roles = user.roles
    message = ""
    for role in roles:
        message += f'{role.name}:\n\t{[permission.name for permission in role.permissions]}\n'
    await ctx.send(message, ephemeral=True)

@slash_command(name="print_ban_list", description="**ADMIN**: Get information about banlist")
async def print_ban_list(ctx: SlashContext):
    await ctx.guild.gateway_chunk()
    message = ""
    if not BAN_LIST:
        message = "No ban candidates"
    else:
        for user in BAN_LIST:
            message += f'{user.handle} -> {user.get_duration()}\n'
    await ctx.send(message, ephemeral=True)

@slash_command(name="print_banned_list", description="**ADMIN**: Get information about banned users")
async def print_banned_list(ctx: SlashContext):
    await ctx.guild.gateway_chunk()
    message = ""
    if not BANNED:
        message = "No banned users"
    else:
        for user in BANNED:
            message += f'{user.handle} -> {user.end_date}\n'
    await ctx.send(message, ephemeral=True)
##########################################################################################

# SLASH COMMANDS #
################################################################################
@slash_command(name="gasparko", description="Better hope it's not cold outside")
async def gasparko(ctx: SlashContext):
    if await admin_checker(ctx):
        return

    value = randint(-20, 100)

    curr_user = get_user(ctx.member.id, GASPARKO_LIST)
    if curr_user:
        await ctx.send(f'You already measured your gasparko today, dummy <:pocem:1037501105774538863> it was {curr_user.get_duration()}cm', ephemeral=True)
        return
    else:
        GASPARKO_LIST.append(User(ctx.member.id, ctx.member.display_name, 0, value, 0, ctx.member))

    emote = ""
    if value > 80:
        emote = '<:peknyNazorBrasko:1041866001714778152>'
    elif value > 60:
        emote = '<:feesPekne:1042562085785182310>'
    elif value > 40:
        emote = '<:velkaRadost:1169613223734026253>'
    elif value > 20:
        emote = ':nerd:'
    elif value > 10:
        emote = '<:sikana:1076611866039693372>'
    elif value > 0:
        emote = ':woman:'
    else:
        emote = '<:klasika:1070481083084328970>'
    await ctx.send(f'{value}cm {emote}')

@slash_command(name="gasparko_tierlist", description="Who had the biggest gasparko today?")
async def gasparko_tierlist(ctx: SlashContext):
    await ctx.send(print_gasparko_tierlist(GASPARKO_LIST))

@slash_command(name="voteban", description="Vote to ban user")
@slash_option(name="naughty_boy", description="Someone about to get banned", required=True, opt_type=OptionType.USER)
@slash_option(name="hours", description="Time in hours", required=True, opt_type=OptionType.INTEGER, min_value=1, max_value=24)
async def voteban(ctx: SlashContext, naughty_boy: Member, hours: int):
    await ctx.guild.gateway_chunk()
    
    if await admin_checker(ctx):
        return

    if naughty_boy.id == ctx.member.id:
        await ctx.send(f'You can\'t ban yourself, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return

    if naughty_boy.id == BOT.user.id:
        await ctx.send(f'You can\'t ban the bot, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return

    if naughty_boy.id not in [human.id for human in ctx.guild.humans]:
        await ctx.send(f'You can only ban people from this server, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return

    if BAN_ROLE in [role.id for role in naughty_boy.roles]:
        await ctx.send(f'User {naughty_boy.display_name} already banned, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return

    curr_user = get_user(naughty_boy.id, BAN_LIST)
    if curr_user:
        if curr_user.voter_is_present(ctx.member.id):
            await ctx.send(f'You already voted to ban {naughty_boy.display_name}, dummy <:pocem:1037501105774538863>', ephemeral=True)
            return
        curr_user.update_stats(naughty_boy.display_name, ctx.member.id, hours)
    else:
        BAN_LIST.append(User(naughty_boy.id, naughty_boy.display_name, ctx.member.id, hours, len(ctx.guild.humans), naughty_boy))

    await ctx.send(f'{ctx.member.display_name} voted to ban {naughty_boy.display_name} for {hours}h\n\n{print_stats(BAN_LIST)}')

    curr_user = get_user(naughty_boy.id, BAN_LIST)
    if curr_user.is_bannable():
        await ban(curr_user, ctx, "Banned {user} until {date}")

@slash_command(name="unvoteban", description="Redact your vote to ban a particular user")
@slash_option(name="naughty_boy", description="Someone you don't want to ban anymore", required=True, opt_type=OptionType.USER)
async def unvoteban(ctx: SlashContext, naughty_boy: Member):
    if not BAN_LIST:
        await ctx.send("Nobody to unvoteban, dummy <:pocem:1037501105774538863>", ephemeral=True)

    curr_user = get_user(naughty_boy.id, BAN_LIST)
    try:
        del curr_user.voters[ctx.member.id]
        curr_user.decrease_vote()
        if not curr_user.voters:
            BAN_LIST.pop(BAN_LIST.index(curr_user))
        await ctx.send("Okay <:velkaRadost:1169613223734026253>", ephemeral=True)
    except Exception:
        await ctx.send(f'You didn\'t vote to ban this user, dummy <:pocem:1037501105774538863>', ephemeral=True)

@slash_command(name="self_unverify", description="For nerds; ban yourself for a given time period")
@slash_option(name="hours", description="Time in hours", required=True, opt_type=OptionType.INTEGER, min_value=1, max_value=24)
async def self_unverify(ctx: SlashContext, hours: int):
    if await admin_checker(ctx):
        return

    # this is a bit stupid, might need a rework, works tho
    curr_user = get_user(ctx.member.id, BAN_LIST)
    if curr_user:
        BAN_LIST.pop(BAN_LIST.index(curr_user))
    # required for ban() function
    BAN_LIST.append(User(ctx.member.id, ctx.member.display_name, ctx.member.id, hours, 0, ctx.member))
    curr_user = get_user(ctx.member.id, BAN_LIST)
    tmp = await ctx.send("Alright", ephemeral=True)
    await ban(curr_user, ctx, "{user} self unverified until {date}")
    await ctx.delete(tmp)

@slash_command(name="time_left", description="How long until I get unbanned?")
async def time_left(ctx: SlashContext):
    # special admin check
    if not get_user(ctx.member.id, BANNED) and ctx.guild.is_owner(ctx.member.id):
        await ctx.send(f'{ctx.member.display_name} stop it, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return

    diff = str(get_user(ctx.member.id, BANNED).end_date - datetime.now())

    # past end_time, waiting for task to unban user
    if "-1 day" in diff:
        await ctx.send("Any time now...", ephemeral=True)
        return
    times = diff.split('.')[0].split(':') # input looks like "23:52:15.66424"
    await ctx.send("You will be banned for {} hours, {} minutes and {} seconds".format(*[int(time) for time in times]), ephemeral=True)

@slash_command(name="voteban_stats", description="How many votes does each bannee have?")
async def voteban_stats(ctx: SlashContext):
    if await admin_checker(ctx):
        return
    if BAN_LIST:
        message = print_stats(BAN_LIST)
    else:
        message = "There currently are no votes"
    await ctx.send(message)
################################################################################

# NEWS TELLER #
###########################################################################
@slash_command(name="whats_new", description="What are some new features?")
async def whats_new(ctx: SlashContext):
    with open("changelog.md", 'r') as cl:
        # please, after any behavior changing contribution, mention yourself in the changelog
        # and add {"your_username": ctx.guild.get_member(your_user_id).display_name} into the .format dict
        # and {your_username} field into the changelog
        await ctx.send(cl.read().format(**{"bot_name": BOT.user.mention})) # fill modular fields in changelog
###########################################################################

@listen()
async def on_message_create(event: MessageCreate):
    if event.message.author == BOT.user:
        return

    words = event.message.content.lower().split(" ")
    tag = False

    # naughty
    for word in words:
        # fuck this regex in particular
        if search(r"^n+([ehiy]+|ay|ey|io|[il]+)[gq$]+h?(a+|aer|a+h+|a+r+|e+|ea|eoa|e+r+|ie|ier|let|lit|o|or|r+|u|uh|uhr|u+r+|ward|y+)s*$", word):
            tag = True
            if not any(x in word for x in GOOD_NWORDS):
                await event.message.channel.send(":warning:")
                return
    if tag:
        await event.message.add_reaction("<:pampolicaj:1065346947734577266>")

    # message nerder
    # if event.message.author.id == NERD_USER:
    #     await event.message.add_reaction("\U0001F913")

    if "gemini" in words or "geminis" in words:
        await event.message.channel.send("Damn right gurl :nail_care: :nail_care: :nail_care:")
 
    # oops
    if "cp" in words:
        picked = choice(CP_OPTS)
        await event.message.channel.send(f'Did you mean {picked}? :thinking:')
        if picked == "child porn":
            await event.message.channel.send(f'YOU DID IT {event.message.author.mention} :partying_face:')

@listen()
async def on_startup():
    for guild in BOT.guilds:
        await guild.gateway_chunk()
    await BOT.get_channel(BOT_ROOM).send(f'{BOT.user.mention} **ONLINE**, I\'m back bitches <:peknyNazorBrasko:1041866001714778152>')
    await BOT.change_presence(activity=Activity(name="deez nuts", type=ActivityType.WATCHING))
    for sig in [SIGINT, SIGTERM]:
        get_event_loop().add_signal_handler(sig, lambda sig=sig: create_task(sig_handler(sig)))

    # START TASKS #
    ###################
    check_unban.start()
    reset.start()
    ###################

BOT.start(TOKEN)