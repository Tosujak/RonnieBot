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
from fsm import nword_fsm

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
           "cerebral palsy",
           "collosal pipik"]

GOOD_NWORDS = ["niggard",
               "niggerf",
               "nigger-f",
               "niggl",
               "snigger"]

nword_room_counters = {}  # format: roomID: counter

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


# totalny bordel, might edit later ked to setupnem v IDE xd#

iksde = ['Milovala si ma viem.', 'Ty a ja, náš malý sen', 'a ja som ti sľúbil, že ťa neopustím, neodídem.', 'Závidia nám to čo máme, na knihu romantickú námet.', 'Kto by to bol povedal, že jedného dňa jej budem písať záveť.', 'Kráľovná a kráľ, tvoríme dokonalý pár', 'to čo prežívame spolu je ako z rozprávkových strán.', 'Ja mám krídla, ty chceš lietať, ty sa pozrieš a ja viem kam,', 'len s tebou poletím aj keď sa bojím výšok, lietam.', 'Som stratený v oblakoch, lietam len s ňou,', 'len s tebou láska ten život je hrou.', 'Sľúbim ti všetko len ostaň so mnou.', 'Len s tebou navždy, nepôjdem za inou.', 'Ale jak už býva zvykom, tak jeden posere to a pochová vzťah.', 'Idem za inou na teba zabúdam a bez výčitiek mením plán nám a', 'Cítiš sa ako v zlom sne,', 'keď mením meno, mením posteľ', 'a odchádzam na breh a ty tam stojíš sama na zapálenom moste.', 'Raz bol jeden kráľ, čo kráľovstvo mal', 'pre pár nocí s inou sa kráľovny vzdal.', 'Raz bol jeden kráľ, sa žobrákom stal', 'keď kráľovstvo padá, svet nocí nastal.', 'Červený koberec pre všetkých, V.I.P. lístkami nešetrím.', 'Na zámky pozvánky poslané, každý netvor je na zozname', 'Doktor Jekkyl a Mr.Hyde, rozhýbe hviezdy aj celý kraj', 'Nič sa už nepýtaj,dôjdi si potykať vyleští kopytá zapriahni koníka', 'prid prdele pochytať, hudba k nám preniká,', 'noc už je opitá víta ťa, gotika,', 'aj a-a-a-anjeli prileteli,tí-í-í-í-í čo ich v nebi nechceli', 'Chceš vidět méně reklam? Registruj se', 'Každááápríšera vstáva keď hudba hrá nám', 'z hrobky do tmy sa vynára neloví,dnes neloví, dnes užíva si Halloween.', 'Plná sála žije do rána, do hudby od Petra Pánna', 'celé peklo na jednej vlne žijeme kým je mesiac v splne.', 'Nalievaj,tak nalievaj nech sa nám krv v tele zahrieva', 'pripíjam na smrť a na jej účel, kým necítim smrteľné lúče', 'Neprepadáva ma tá nostalgia, vôbec ne,', 'preto sa tak často vracám mysľou v čase naspäť,', 'no výpady čo dali sme sú mega povestné,', 'nechápem jak prežili sme, blbí majú šťastie,', 'každý pátek, ktorý vyrazil sa do klubov,', 'ženy ostali doma, neveštil žiadne dobré správy,', 'potvrdí každý jeden alkoholik čo tu bol,', 'legendárna veta v nedeľu: Zas sme to dojebali', 'Vlak Spišan na to kupé, show sa zmenilo na psychiatriu, asi sanitku zavoláme,', 'ľudia opúšťajú kupéčko, keď sa im pred očami objavujú vajca na skle maľované,', 'už pri Trnave je jasné, že, tento víkend bude kaša, o jednej sme sa už dole dali,', 'celá posádka už dosť vie že, v nedeľu budeme hovoriť o tom jak sme to dojebali', 'Na mindž rozdrbané hotelové izby,', 'zasa sme to čooo?', 'Zasa sme to dojebali!', 'Doma nás čaká vytočený grizly,', 'Čierna diera a my sme v nej zmizli,', 'Netušil som, že to je tak tvrdý biznis, chcel som iba rapovať, o tomto mi nepovedali ', 'Kamenica - Imperko, dnes sa tu nenajebem,', 'držím sa, nepovolím, aj keď ma Slavo prehovára,', 'dojde Škafo, hovorí dajme si za jeden,', 'Bermudský trojuholník - svoju bránu mi otvára,', 'kapurkova 20x, starý, nerob mi,', 'o osmej ráno chcem vyraziť, nechcem byť jak tupelo,', 'vonku svitá, ja začínam byť nervózny,', 'mal som prísť v nedeľu ráno, zas dojdeme v pondelok!', 'V Senici ma nevedeli hodinu zobudiť,', 'lebo začali sme u Čiča už 7 hodín predtým,', 'V Raslaviciach šipka do davu ktorý sa zľakol, toho Moby dicka takže som sa zjebal medzi všetkých,', 'zlomený jak vzduchovka, prehodený cez fotelu,', 'v klube majiteľ sa pýta Čiča, či to dám,', 'Nebojte nič, šefko Kali iba medituje, zaručujem, že tú show zajebe jak pán!', 'Swag, fame, fake, hate...nepoužívam tie slová aj tak je mi hej', 'Prečo ne?...aj keď sú to TOP slová na burze, amatér aj bez nich je stále viac v kurze', 'Prečo ne?..povedať to čo aj tak chápu, že moje špičky im na paty stále viacej šlapú', 'Prečo nebyť šťastný, keď som hrozbou pre nich, 3 roky a štvrtý album, stále iba tréning', 'Prečo nespomenúť, že rádio ma stoplo, bo preletel som stropom, toho čo bolo top v ňom', 'Prečo nepovedať, že majú strach, že majú tlak a že sa majú čoho báť', 'A prečo ne?..prečo ich na to nepripraviť, to čo bude nasledovať im naruší plány', 'Som vďačný a pokorný, so sebou spokojný, môžte tlačiť na dvere, aj tak si ich otvorím', 'mám prázdne vajcá', 'pozitívne naladený už od rána', 'primitívny úsmev, aj keď hubu neotváram', 'škerím sa na každého, aj keď sa nerozprávam', 'radšej nech je deň jak komédia a ne dráma', 'žijem v bubline, ktorá sa iným nepozdáva', 'na svoj život jedine ja vlastním všetky práva', 'preto nemám tlak z toho, keď sa ohovára', 'jediné tlaky čo mám sú, keď sa ozve káva', 'mám povahu čo dokáže ludí nasrať', 'každý názor proti prúdu, nerobím to naschvál', 'z rád čo dávajú mi vždy sa mi chce zaspať', 'a deje sa to stále, aj keď som už prestal chlastať', 'nechce sa mi počúvať, nebavia ma názory', 'pomaly sa posúvam, nechce sa mi závodiť', 'nedokážem poslúchať, dvíham si tie závory', 'proste žijem tak, ako keď máme, máš, mám', 'okná dole, ruka venku v pravom pruhu dvadsať', 'robím iba tolko koľko treba, žiadny nadčas', 'zariadil som si to tak, aby som mohol mať čas', 'nenaháňam sa už, lebo treba zabávať sa', 'flegma vo mne žije na sto percent', 'proste neurobím to, čo sa mi robiť nechce', 'a nevadí, že som neuspel v ich dospelom teste', 'preto počúvam, že moje chovanie je detské', 'nevadí nevadí nevadí', 'na ich názor neni som zvedavý', 'žiť jak oni chcú ma nebaví', 'a keď ma to nebaví preladím', 'zo života nerobím si kardio', 'a nepúšťam si k sebe žiadne hovná', 'negatívne typy držím si ďalej odo mňa']

@slash_command(name="kali_pomoc", description="Kali ti pomoze")
async def kali_pomozmi(ctx: SlashContext):
    await ctx.send(choice(iksde))

@slash_command(name="kali", description="Raz bol jeden kral")
async def kali_pesnic(ctx: SlashContext):
    await ctx.send("""Milovala si ma viem.
Ty a ja, náš malý sen
a ja som ti sľúbil, že ťa neopustím, neodídem.
Závidia nám to čo máme, na knihu romantickú námet.
Kto by to bol povedal, že jedného dňa jej budem písať záveť.
Kráľovná a kráľ, tvoríme dokonalý pár
to čo prežívame spolu je ako z rozprávkových strán.
Ja mám krídla, ty chceš lietať, ty sa pozrieš a ja viem kam,
len s tebou poletím aj keď sa bojím výšok, lietam.
Som stratený v oblakoch, lietam len s ňou,
len s tebou láska ten život je hrou.
Sľúbim ti všetko len ostaň so mnou.
Len s tebou navždy, nepôjdem za inou.
Ale jak už býva zvykom, tak jeden posere to a pochová vzťah.
Idem za inou na teba zabúdam a bez výčitiek mením plán nám a
Cítiš sa ako v zlom sne,
keď mením meno, mením posteľ
a odchádzam na breh a ty tam stojíš sama na zapálenom moste.
Raz bol jeden kráľ, čo kráľovstvo mal
pre pár nocí s inou sa kráľovny vzdal.
Raz bol jeden kráľ, sa žobrákom stal
keď kráľovstvo padá, svet nocí nastal.""")
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

    # naughty
    for word in words:
        if any(x in word for x in GOOD_NWORDS):
            await event.message.add_reaction("<:pampolicaj:1065346947734577266>")
        # fuck this regex in particular
        elif search(r"^n+([ehiy]+|ay|ey|io|[il]+)[gq$]+h?(a+|aer|a+h+|a+r+|e+|ea|eoa|e+r+|ie|ier|let|lit|o|or|r+|u|uh|uhr|u+r+|ward|y+)s*$", word):
            await event.message.channel.send(":warning:")
            return

    # naughty char by char
    global nword_room_counters
    # if it doesnt exist, create a new channel entry in the counter dict
    if not event.message.channel.id in nword_room_counters.keys():
        nword_room_counters[event.message.channel.id] = 0
    nword_counter = nword_room_counters[event.message.channel.id]
    
    is_counter_filled, new_state = nword_fsm(nword_counter, words[0])
    if is_counter_filled:
        # reset counter for given room and send warning msg
        nword_room_counters[event.message.channel.id] = 0  
        await event.message.channel.send(":warning::warning::warning:")
        return
    else:
        nword_room_counters[event.message.channel.id] = new_state
    print(nword_room_counters)
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

    # povedz lod
    if "lod" in words and "povedz" not in words:
        await event.message.channel.send("Do pici chod <:pocem:1037501105774538863>")

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

print(f"[{datetime.now().strftime('%H:%M:%S')}]: Starting the bot")
BOT.start(TOKEN)
