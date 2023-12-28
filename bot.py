from os import getenv
from dotenv import load_dotenv
from random import randint, choice
from datetime import datetime, timedelta
from interactions import (Client, Intents, Status, Permissions, SlashContext, Member, Task, IntervalTrigger, OptionType, 
                          listen, slash_command, slash_option, slash_default_member_permission)
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
           "cunt piercing"]

async def ban(bannee: User):
    # bannee.end_date = datetime.now() + timedelta(seconds=20) # TODO fix
    bannee.end_date = datetime.now() + timedelta(hours=bannee.get_duration())
    await bannee.instance.add_role(BAN_ROLE)
    await bannee.instance.remove_role(NORMAL_ROLE)
    BAN_LIST.pop(BAN_LIST.index(bannee))
    BANNED.append(bannee)
    return f'Banned {bannee.instance.display_name} until {bannee.end_date}'

async def check_unban():
    unbanned = []
    for bannee in BANNED:
        if bannee.end_date < datetime.now():
            await bannee.instance.remove_role(BAN_ROLE)
            await bannee.instance.add_role(NORMAL_ROLE)
            unbanned.append(BANNED.index(bannee))
    for i in unbanned:
        BANNED.pop(i)

@slash_command(name="gasparko", description="Better hope it's not cold outside")
@slash_default_member_permission(Permissions.VIEW_CHANNEL)
async def gasparko(ctx: SlashContext):
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

@slash_command(name="online", description="Get information about online users")
@slash_default_member_permission(Permissions.MANAGE_EMOJIS_AND_STICKERS)
async def online(ctx: SlashContext):
    await ctx.guild.gateway_chunk()
    reply = ""
    for member in ctx.guild.humans:
        reply += f'{member.display_name} => {member.status}\n'
    reply += f'Total: {len([m for m in ctx.guild.humans if m.status and m.status != Status.OFFLINE])}'
    await ctx.send(reply, ephemeral=True)

@slash_command(name="voteban", description="Vote to ban user")
@slash_option(name="naughty_boy", description="Someone about to get banned", required=True, opt_type=OptionType.USER)
@slash_option(name="hours", description="Time in hours", required=True, opt_type=OptionType.INTEGER, min_value=1, max_value=24)
@slash_default_member_permission(Permissions.VIEW_CHANNEL)
async def voteban(ctx: SlashContext, naughty_boy: Member, hours: int):
    await ctx.guild.gateway_chunk()
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
        message = await ban(curr_user)
        await ctx.guild.get_channel(VAZENIE_ROOM).send(message)
        await ctx.guild.get_channel(ctx.channel_id).send(message)

    # await ctx.send(f'{ctx.guild.get_member(naughty_boy.id).mention}')

# @interactions.slash_command(name="voteunban", description=)
# TODO check if user can unvote by checking if he is in the voter list


@listen()
async def on_message_create(event: MessageCreate):
    if event.message.author == BOT.user:
        return
    
    # message nerder
    # if event.message.author.id == NERD_USER:
    #     await event.message.add_reaction("\U0001F913")

    # oops
    if "cp" in event.message.content.lower():
        await event.message.channel.send(f'Did you mean {choice(CP_OPTS)}? :thinking:')

    # pretty self explanatory
    mssg = event.message.content.lower()
    if "nigg" in mssg or "negger" in mssg or "neger" in mssg:
        await event.message.channel.send(":warning:")

@listen()
async def on_startup():
    print("Bot ready")
    Task(check_unban, IntervalTrigger(minutes=30)).start()

BOT.start(TOKEN)