from os import getenv
from re import search
from dotenv import load_dotenv
from random import randint, choice
from datetime import datetime, timedelta
from interactions import (Client, Intents, Status, SlashContext, Member, Task, IntervalTrigger, OptionType, Activity, ActivityType, 
                          listen, slash_command, slash_option)
from interactions.api.events import MessageCreate

# Custom lib
from user import User, get_user, print_stats

load_dotenv()

TOKEN = getenv("TOKEN")
NERD_USER = int(getenv("NERD_USER"))
BAN_ROLE = int(getenv("BAN_ROLE"))
NORMAL_ROLE = int(getenv("NORMAL_ROLE"))
VAZENIE_ROOM = int(getenv("VAZENIE_ROOM"))
BAN_LIST = []
BANNED = []

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

async def ban(bannee: User):
    bannee.end_date = datetime.now() + timedelta(hours=bannee.get_duration())
    await bannee.instance.add_role(BAN_ROLE)
    await bannee.instance.remove_role(NORMAL_ROLE)
    BAN_LIST.pop(BAN_LIST.index(bannee))
    BANNED.append(bannee)

async def check_unban():
    unbanned = []
    for bannee in BANNED:
        if bannee.end_date < datetime.now():
            await bannee.instance.remove_role(BAN_ROLE)
            await bannee.instance.add_role(NORMAL_ROLE)
            unbanned.append(BANNED.index(bannee))
    for i in unbanned:
        BANNED.pop(i)

async def admin_checker(ctx: SlashContext):
    if BAN_ROLE in [role.id for role in ctx.member.roles] and ctx.guild.is_owner(ctx.member.id):
        await ctx.send(f'{ctx.member.display_name} stop it, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return True
    else:
        return False

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
##########################################################################################

@slash_command(name="gasparko", description="Better hope it's not cold outside")
async def gasparko(ctx: SlashContext):
    if await admin_checker(ctx):
        return
    value = randint(-20, 100)
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

@slash_command(name="voteban", description="Vote to ban user")
@slash_option(name="naughty_boy", description="Someone about to get banned", required=True, opt_type=OptionType.USER)
@slash_option(name="hours", description="Time in hours", required=True, opt_type=OptionType.INTEGER, min_value=1, max_value=24)
async def voteban(ctx: SlashContext, naughty_boy: Member, hours: int):
    await ctx.guild.gateway_chunk()
    
    if await admin_checker(ctx):
        return

    active_users = len([m for m in ctx.guild.humans if m.status and m.status != Status.OFFLINE])

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
        curr_user.update_stats(naughty_boy.display_name, ctx.member.id, hours, active_users)
    else:
        BAN_LIST.append(User(naughty_boy.id, naughty_boy.display_name, ctx.member.id, hours, active_users, naughty_boy))

    await ctx.send(print_stats(BAN_LIST))

    curr_user = get_user(naughty_boy.id, BAN_LIST)
    if curr_user.is_bannable():
        await ban(curr_user)
        message = f'Banned {curr_user.instance.display_name} until {curr_user.end_date}'
        await ctx.guild.get_channel(VAZENIE_ROOM).send(message)
        await ctx.guild.get_channel(ctx.channel_id).send(message)

    # await ctx.send(f'{ctx.guild.get_member(naughty_boy.id).mention}')

# @interactions.slash_command(name="voteunban", description=)
# TODO check if user can unvote by checking if he is in the voter list

@slash_command(name="self_unverify", description="For nerds; ban yourself for a given time period")
@slash_option(name="hours", description="Time in hours", required=True, opt_type=OptionType.INTEGER, min_value=1, max_value=24)
async def self_unverify(ctx: SlashContext, hours: int):
    if await admin_checker(ctx):
        return

    BAN_LIST.append(User(ctx.member.id, ctx.member.display_name, ctx.member.id, hours, 0, ctx.member))
    curr_user = get_user(ctx.member.id, BAN_LIST)
    await ban(curr_user)
    message = f'{curr_user.instance.display_name} self unverified until {curr_user.end_date}'
    await ctx.guild.get_channel(VAZENIE_ROOM).send(message)
    await ctx.guild.get_channel(ctx.channel_id).send(message)

@slash_command(name="time_left", description="How long until I get unbanned?")
async def time_left(ctx: SlashContext):
    # admin check
    if BAN_ROLE not in [role.id for role in ctx.member.roles] and ctx.guild.is_owner(ctx.member.id):
        await ctx.send(f'{ctx.member.display_name} stop it, dummy <:pocem:1037501105774538863>', ephemeral=True)
        return
    await ctx.send(f'You will be banned until {get_user(ctx.member.id, BANNED).end_date}', ephemeral=True)

@slash_command(name="voteban_stats", description="How many votes does each bannee have?")
async def voteban_stats(ctx: SlashContext):
    if await admin_checker(ctx):
        return
    if BAN_LIST:
        message = print_stats(BAN_LIST)
    else:
        message = "There currently are no votes"
    await ctx.send(message)

# NEWS TELLER #
###########################################################################
@slash_command(name="whats_new", description="What are some new features?")
async def whats_new(ctx: SlashContext):
    message = "DEEZ NUTS... but now for real:\
        \r\t1) **/whats_new** - describes some new features, get more detail by invoking the **/whats_new** command || fuck recursion <:pocem:1037501105774538863> ||\
        \r\t2) **/voteban_stats** - shows current vote count for each ban candidate\
        \r\t3) **/self_unverify** - bans you for a given time period set by you\
        \r\t4) **/time_left** - shows when you will be unbanned, you need to be banned to see that tho"
    await ctx.send(message)
###########################################################################

@listen()
async def on_message_create(event: MessageCreate):
    if event.message.author == BOT.user:
        return

    message = event.message.content.lower()
    tag = False

    # naughty
    for word in message.split(" "):
        if search(r"n+([ehiy]+|ay|ey|io|[il]+)[gq$]+h?(a+|aer|a+h+|a+r+|e+|ea|eoa|e+r+|ie|ier|let|lit|o|or|r+|u|uh|uhr|u+r+|ward|y+)s*", word):
            tag = True
            if not any(x in word for x in GOOD_NWORDS):
                await event.message.channel.send(":warning:")
                return
    if tag:
        await event.message.add_reaction("<:pampolicaj:1065346947734577266>")

    # message nerder
    # if event.message.author.id == NERD_USER:
    #     await event.message.add_reaction("\U0001F913")

    if "gemini" in message.split(" "):
        await event.message.channel.send("Damn right gurl :nail_care: :nail_care: :nail_care:")
 
    # oops
    if "cp" in message.split(" "):
        await event.message.channel.send(f'Did you mean {choice(CP_OPTS)}? :thinking:')

@listen()
async def on_startup():
    print("Bot ready")
    for guild in BOT.guilds:
        await guild.gateway_chunk()
    await BOT.change_presence(activity=Activity(name="deez nuts", type=ActivityType.WATCHING))
    Task(check_unban, IntervalTrigger(minutes=1)).start()

BOT.start(TOKEN)