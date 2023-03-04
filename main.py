import asyncio
import json
import re

from interactions.ext.wait_for import setup
from interactions.ext.persistence import PersistentCustomID
import models.queries as queries
import interactions
import settings

bot = interactions.Client(
    token=settings.DISCORD_TOKEN,
    default_scope=966828980999180288,
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.ALL
)

bot.load("interactions.ext.persistence", cipher_key = 'E922EF827C3AD0F62C55068A4EC18597')

setup(bot)

@bot.event
async def on_ready():
    print('ready')
    query = queries.fetch_all_info_messages()
    global info_messages
    info_messages = query['data']

@bot.command(
    name="reload_db",
    description="TBD"
)
async def reload_db(ctx: interactions.CommandContext):
    query = queries.fetch_all_info_messages()
    info_messages = query['data']
    await ctx.send("DB reloaded")


@bot.command(
    name="register",
    description="TBD",
    options=[
        interactions.Option(
            name="name",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def register(ctx: interactions.CommandContext, name: str, ):
    if not all(char.isalpha() or char.isspace() for char in name): return await ctx.send(info_messages['char_register_invalid_name'])
    message = queries.insert_user_and_character(str(ctx.author.id), name, {'lvl': '966878470305087507'})
    if not message['status']: return await ctx.send(info_messages[message['data']]) #"char_register_limit", "char_register_duplicate_name"
    await ctx.send(info_messages[message['data']], ephemeral=True) #"char_register_success"
    await ctx.author.modify(roles=[966878470305087507])
    await ctx.author.modify(nick=name)
    log_channel = await interactions.get(bot, interactions.Channel, object_id=1068677341926137967)
    await log_channel.send(info_messages['log_register_success'].format(ctx.author.mention, name))


@bot.command(
    name="charselect",
    description="TBD",
)
async def charselect(ctx: interactions.CommandContext):
    char_list = []
    db_char_list = queries.fetch_all_characters_by_id(str(ctx.author.id))['data']
    for char in db_char_list:
        char_list.append(interactions.SelectOption(label=char['name'], value=char['id']))
    select_menu = interactions.SelectMenu(
        custom_id="selectmenu",
        options=char_list,
        placeholder="Selecione o seu personagem",
        min_values=1,
        max_values=1,
    )
    await ctx.send(components=select_menu, ephemeral=True)


@bot.component("selectmenu")
async def selectchar(ctx: interactions.ComponentContext, user=None):
    char = queries.fetch_character_by_id_and_insert_active_character(ctx.data.values[0])['data'][0]
    current_nick = ctx.author.nick
    roles = json.loads(char['roles_id'])
    role_list = []
    for roleid in roles.values():
        role_list.append(int(roleid))
    await ctx.author.modify(roles=role_list)
    await ctx.author.modify(nick=char['name'])
    await ctx.send(info_messages['char_swap'].format(char['name']), ephemeral=True)


@bot.command(
    name="hero",
    description="TBD",
    options=[
        interactions.Option(
            name="link",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def hero(ctx: interactions.CommandContext, link: str):
    if not bool(re.match("https://www.heroforge.com/load_config.*", link)):
        return await ctx.send(info_messages['char_hfimport_invalid'], ephemeral=True)
    insert = queries.insert_hero_link(str(ctx.author.id), link)
    if not insert['status']: return await ctx.send(info_messages[insert['data']], ephemeral=True) #"char_hfimport_duplicate_link"
    await ctx.send(info_messages[insert['data']].format(ctx.author.mention), ephemeral=True) #"char_hfimport_success"
    await ctx.send(info_messages['char_register_finished'], ephemeral=True)
    await ctx.send(info_messages['server_char_register_finished'].format(ctx.author.mention))


@bot.command(
    name="beyond",
    description="TBD",
    options=[
        interactions.Option(
            name="link",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def beyond(ctx: interactions.CommandContext, link: str):
    if not bool(re.match("https://www.dndbeyond.com/characters/.*", link)):
        return await ctx.send(info_messages['char_dndbimport_invalid_link'], ephemeral=True)
    insert = queries.insert_beyond_link(str(ctx.author.id), link)
    if not insert['status']: return await ctx.send(info_messages[insert['data']], ephemeral=True) #"char_dndbimport_duplicate_link"
    await ctx.send(info_messages[insert['data']].format(ctx.author.nick), ephemeral=True) #"char_dndbimport_success"
    log_channel = await interactions.get(bot, interactions.Channel, object_id=1068677341926137967)
    await log_channel.send('/register ' + link)


@bot.command(
    name="register_master",
    description="TBD",
    options=[
        interactions.Option(
            name="id",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def register_master(ctx: interactions.CommandContext, id: str):
    message = queries.insert_master(str(ctx.author.id))
    if not message['status']: return await ctx.send(message['data'])
        #info_messages[message['data']])  #"master_register_duplicate_name"
    #await ctx.send(info_messages[message['data']])
    await ctx.send(message['data'])


@bot.command(
    name="create_mission",
    description="TBD",
    options=[
        interactions.Option(
            name="name",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def create_mission(ctx: interactions.CommandContext, name: str):
    message = queries.insert_mission(str(ctx.author.id), name)
    if not message['status']: return await ctx.send(message['data'])
       # info_messages[message['data']])
    #await ctx.send(info_messages[message['data']])
    await ctx.send(message['data'])


@bot.command(
    name="create_party",
    description="TBD",
    options=[
        interactions.Option(
            name="name",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def create_party(ctx: interactions.CommandContext, name: str):
    message = queries.insert_party(str(ctx.author.id), name)
    if not message['status']: return await ctx.send(message['data'])
    #    info_messages[message['data']])  # "already_in_party"
    #await ctx.send(info_messages[message['data']])
    await ctx.send(message['data'])

@bot.command(
    name="leave_party",
    description="TBD"
)
async def leave_party(ctx: interactions.CommandContext):
    message = queries.leave_party(str(ctx.author.id))
    if not message['status']: return await ctx.send(message['data'])
    #    info_messages[message['data']])  # "not_in_party"
    #await ctx.send(info_messages[message['data']])
    await ctx.send(message['data'])

@bot.command(
    name="invite",
    description="TBD",
    options=[
        interactions.Option(
            name="name",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def invite(ctx: interactions.CommandContext, name):
    invited_player = queries.fetch_user_by_char_name(name)
    if not invited_player['status']:
        return await ctx.send(invited_player['data'])
    receiver_discord_id = invited_player['data']['discord_id']
    user = await interactions.get(bot, interactions.User, object_id=receiver_discord_id)
    user._client = bot._http
    custom_id = json.dumps({"sender_discord_id": str(ctx.author.id), "receiver_discord_id": receiver_discord_id})
    accept_party_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="ACEITAR CONVITE",
        custom_id="teste"
    )

    msg = await user.send(
        "O jogador " + ctx.user.username + " está te convidando para um grupo." + " O que deseja fazer?",
        components=[accept_party_button])

    try:
        button_ctx: interactions.ComponentContext = await bot.wait_for_component(components=accept_party_button, timeout=15)
        queries.join_party(str(ctx.author.id), receiver_discord_id)
        await button_ctx.send("Aceito")
        await msg.delete()

    except asyncio.TimeoutError:
        # When it times out, edit the original message and remove the button(s)
        return await msg.delete()


@bot.command(
    name="mission_complete",
    description="TBD"
)
async def mission_complete(ctx: interactions.CommandContext):
    mission = queries.process_mission(str(ctx.author.id))
    if not mission['status']: return await ctx.send(mission['data'])
    #    info_messages[mission['data']])  # "no_active_mission"
    mission_spec = mission['specs']


@bot.command(
    name="mission_fail",
    description="TBD"
)
async def mission_fail(ctx: interactions.CommandContext, mission_id: int):
    await ctx.send("mamaram")

@bot.command(
    name="teste",
    description="TBD"
)
async def teste(ctx: interactions.CommandContext):
    print(queries.teste(str(ctx.author.id)))

@bot.command(
    name="patreon",
    description="Mudar o status do patreon",
    options=[
        interactions.Option(
            name="discord_id",
            description="Discord ID do usuário",
            type=interactions.OptionType.STRING,
            required=True,
            min_length=18,
            max_length=18
        ),
    ],
)
async def patreon(ctx: interactions.CommandContext, discord_id: str):
    give_custom_id = PersistentCustomID(bot, "give-patreon", {'id': discord_id, 'action': 'give'})
    remove_custom_id = PersistentCustomID(bot, "remove-patreon", {'id': discord_id, 'action': 'remove'})
    give_patreon_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="ATIVAR PATREON",
        custom_id=str(give_custom_id),
    )
    remove_patreon_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="DESATIVAR PATREON",
        custom_id=str(remove_custom_id),
    )

    current_patreon_status = queries.check_if_is_patreon(discord_id)
    if not current_patreon_status['status']: return await ctx.send(current_patreon_status['data'], ephemeral=True)

    message = "**ATIVADO**" if current_patreon_status['data'] == 1 else "**DESATIVADO**"

    user = await interactions.get(bot, interactions.User, object_id=discord_id)
    await ctx.send("O usuário " + user.username + " está com o Patreon " + message + ". O que deseja fazer?", components=[give_patreon_button, remove_patreon_button], ephemeral=True)


@bot.persistent_component("give-patreon")
@bot.persistent_component("remove-patreon")
async def change_patreon_status(ctx, package):
    patreon_status = 1 if package['action'] == "give" else 0
    message = "**ATIVADO**" if patreon_status == 1 else "**DESATIVADO**"

    update = queries.update_patreon(package['id'], patreon_status)
    if not update['status']: return await ctx.send(update['data'], ephemeral=True)
    await ctx.send("Patreon " + message + " com sucesso", ephemeral=True)


bot.start()
