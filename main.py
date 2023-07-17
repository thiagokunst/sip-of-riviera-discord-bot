import asyncio
import json
import re
import random

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
    await ctx.send(info_messages['char_register_image'], ephemeral=True)
    await ctx.send(info_messages['char_register_next_step'], ephemeral=True) #"char_register_success"
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
    if not bool(re.match("https://www.heroforge.com/.*", link)):
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
    await ctx.send(info_messages['char_dndbimport_image1'], ephemeral=True) #"char_dndbimport_success"
    await ctx.send(info_messages['char_dndbimport_image2'], ephemeral=True) #"char_dndbimport_success"
    await ctx.send(info_messages['char_dndbimport_next_step'], ephemeral=True) #"char_dndbimport_success"
    log_channel = await interactions.get(bot, interactions.Channel, object_id=1068677341926137967)
    await log_channel.send('/register ' + link)


@bot.command(
    name="register_master",
    description="TBD",
    options=[
        interactions.Option(
            name="discord_id",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def register_master(ctx: interactions.CommandContext, discord_id: str):
    message = queries.insert_master(str(discord_id))
    if not message['status']:
        return await ctx.send(info_messages[message['data']])  #"master_register_duplicate_name"
    await ctx.send(info_messages[message['data']])


@bot.command(
    name="leave_party",
    description="TBD"
)
async def leave_party(ctx: interactions.CommandContext):
    message = queries.leave_party(str(ctx.author.id))
    if not message['status']:
        return await ctx.send(info_messages[message['data']])  # "not_in_party"
    await ctx.send(info_messages[message['data']])

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
@interactions.autodefer()
async def invite(ctx: interactions.CommandContext, name):
    await ctx.defer()
    invited_player = queries.fetch_user_by_char_name(name)
    if not invited_player['status']:
        return await ctx.send(info_messages[invited_player['data']])
    if invited_player['data']['current_party'] is not None:
        return await ctx.send(info_messages["player_already_in_party"])
    receiver_discord_id = invited_player['data']['discord_id']
    user = await interactions.get(bot, interactions.User, object_id=receiver_discord_id)
    user._client = bot._http
    accept_party_id = PersistentCustomID(bot, "accept", {'receiver_discord_id': receiver_discord_id, 'sender_discord_id': str(ctx.author.id)})
    accept_party_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="ACEITAR CONVITE",
        custom_id=str(accept_party_id)
    )
    decline_party_id = PersistentCustomID(bot, "decline", {'receiver_discord_id': receiver_discord_id})
    decline_party_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="RECUSAR CONVITE",
        custom_id=str(decline_party_id)
    )
    actionrow = interactions.ActionRow(components=[accept_party_button, decline_party_button])
    await user.send(
        "O jogador " + ctx.user.username + " está te convidando para um grupo." + " O que deseja fazer?",
        components=actionrow)
    await ctx.send("Solicitação enviada", ephemeral=True)

@bot.persistent_component("accept")
async def manage_invite(ctx, package):
    queries.join_party(package['sender_discord_id'], package['receiver_discord_id'])
    await ctx.message.delete()
    await ctx.send("Convite aceito", ephemeral=True)
@bot.persistent_component("decline")
async def manage_invite(ctx, package):
    await ctx.message.delete()
    await ctx.send("Convite recusado", ephemeral=True)

def sucess_mission_message(mission_data):
    basic_message = "O grupo sucedeu na missão.\n\n"
    if len(mission_data) > 0:
        leveling_info = "\n".join(mission_data)
        final_message = basic_message + leveling_info
        return final_message
    else:
        return basic_message

def fail_mission_message(mission_data):
    basic_message = "O grupo falhou na missão.\n\n"
    if len(mission_data) > 0:
        leveling_info = "\n".join(mission_data)
        final_message = basic_message + leveling_info
        return final_message
    else:
        return basic_message


@bot.command(
    name="mission_end",
    description="TBD",
)
async def mission_end(ctx: interactions.CommandContext):
    success_id = PersistentCustomID(bot, "success", {})
    success_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="SUCESSO",
        custom_id=str(success_id)
    )
    fail_id = PersistentCustomID(bot, "fail", {})
    fail_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="FALHA",
        custom_id=str(fail_id)
    )
    keep_mission_id = PersistentCustomID(bot, "keep", {})
    keep_mission_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="MANTER MISSÃO",
        custom_id=str(keep_mission_id)
    )
    delete_mission_id = PersistentCustomID(bot, "delete", {})
    delete_mission_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="DELETAR MISSÃO",
        custom_id=str(delete_mission_id)
    )
    action_row = interactions.ActionRow(components=[success_button, fail_button])
    action_row2 = interactions.ActionRow(components=[keep_mission_button, delete_mission_button])

    await ctx.send("Declare o resultado da missão", components=action_row, ephemeral=True)
    await ctx.send("Caso decida não narrar mais essa missão, clique em deletar e o canal será deletado em 5 minutos", components=action_row2, ephemeral=True)

@bot.persistent_component("success")
async def mission_success(ctx, package):
    await ctx.defer()
    mission_data = queries.mission_sucess(str(ctx.channel_id))['data']
    mission_end_message = sucess_mission_message(mission_data)
    await ctx.send(mission_end_message)

@bot.persistent_component("fail")
async def mission_success(ctx, package):
    await ctx.defer()
    mission_data = queries.mission_failure(str(ctx.channel_id))['data']
    mission_end_message = fail_mission_message(mission_data)
    await ctx.send(mission_end_message)

@bot.persistent_component("keep")
async def keep_mission(ctx, package):
    await ctx.send("A missão será mantida, selecione uma nova party para fazer a missão", ephemeral=True)
    queries.change_mission_active_party(str(ctx.channel_id), None)

@bot.persistent_component("delete")
async def keep_mission(ctx, package):
    await ctx.send("A missão será deletada em 5 minutos", ephemeral=True)
    queries.delete_mission(str(ctx.channel_id))
    await asyncio.sleep(10)
    channel = await ctx.get_channel()
    await channel.delete()

@bot.command(
    name="char_info",
    description="TBD"
)
async def char_info(ctx: interactions.CommandContext):
    await ctx.send(queries.char_info(str(ctx.author.id)))

@bot.command(
    name="party_info",
    description="TBD"
)
async def party_info(ctx: interactions.CommandContext):
    await ctx.send(queries.party_info(str(ctx.author.id)))


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
@interactions.autodefer()
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



#-------------------------------Comandos-de-narrador-------------------------------------------------------------------#


@bot.command(
    name="create_mission_channel",
    description="TBD",
    options=[
        interactions.Option(
            name="dificuldade",
            description="Nível de dificuldade da missão",
            type=interactions.OptionType.STRING,
            required=True,
        ),
        interactions.Option(
            name="disponibilidade",
            description="Dias disponiveis para narrar no formato d23456s",
            type=interactions.OptionType.STRING,
            required=True,
        )
    ],
)
async def create_mission_channel(ctx: interactions.CommandContext, dificuldade: str, disponibilidade: str):
    if dificuldade.upper() not in ('S', 'SS', 'SSS'):
        return await ctx.send("Dificuldade inválida", ephemeral=True)
    if disponibilidade.lower() not in "d23456s":
        return await ctx.send("Disponibilidade inválida", ephemeral=True)
    await ctx.guild.create_channel(dificuldade+"-"+disponibilidade, interactions.ChannelType.GUILD_TEXT)
    await ctx.send("Descreva a missão e use o comando /create_mission no canal criado", ephemeral=True)


@bot.command(
    name="create_mission",
    description="Criar missão"
)
@interactions.autodefer()
async def create_mission(ctx: interactions.CommandContext):
    master_id = str(ctx.author.id)
    channel_id = str(ctx.channel.id)
    difficulty = len(ctx.channel.name.split('-')[0])
    message = queries.insert_mission(master_id, channel_id, difficulty)
    if not message['status']:
        await ctx.send(info_messages[message['data']], ephemeral=True)
    create_party_custom_id = PersistentCustomID(bot, "create_party", {'channel_id': channel_id})
    create_party_button = interactions.Button(
        style=interactions.ButtonStyle.PRIMARY,
        label="CRIAR GRUPO",
        custom_id=str(create_party_custom_id)
    )
    await ctx.send("Clique aqui para criar um grupo para essa missão", components=create_party_button)

@bot.persistent_component("create_party")
async def apply_to_mission(ctx, package):
    message = queries.insert_party(str(ctx.author.id), str(ctx.channel_id))
    if not message['status']:
        return await ctx.send(info_messages[message['data']], ephemeral=True)  # "create_party_duplicate"

    level = queries.fetch_active_char_data_by_discord_id(ctx.user.id, ['level'])
    if not level['status']:
        return await ctx.send(level['data'], ephemeral=True)
    level = level['data']['level']
    msg = await ctx.send(f"__**{ctx.member.nick}'s Party**__\n\nMembros: \n\n<@{str(ctx.user.id)}> Level: {level}")
    thread = await ctx.guild.create_thread(ctx.member.nick+"'s Party", ctx.channel.id)

    apply_custom_id = PersistentCustomID(bot, "apply", {'party_id': message['data'], 'message_id': str(msg.id), 'host_id': str(ctx.user.id)})
    apply_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="SOLICITAR CONVITE",
        custom_id=str(apply_custom_id)
    )

    channel = await ctx.get_channel()
    last_message_id = channel.last_message_id
    cancel_apply_custom_id = PersistentCustomID(bot, "cancel_apply", [str(ctx.user.id), str(last_message_id), str(msg.id), message['data']]) # host_id=0 #last_message_id=1, message_id=2, party_id=3
    cancel_apply_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="SAIR DO GRUPO",
        custom_id=str(cancel_apply_custom_id)
    )
    actionrow = interactions.ActionRow(components=[apply_button, cancel_apply_button])

    await thread.send("Use os botões para solicitar um convite ou sair do grupo", components=actionrow)


@bot.persistent_component("apply")
async def apply_to_party(ctx, package):
    await ctx.send("Solicitando convite", ephemeral=True)
    party = queries.fetch_party_by_id(package['party_id'])
    if not party['status']:
        return await edit_ephemeral(party['data'], ctx)
    char_info = queries.fetch_active_char_data_by_discord_id(ctx.user.id, ['tb_characters.id', 'level'])
    if not char_info['status']:
        return await edit_ephemeral(char_info['data'], ctx)
    character_id = char_info['data']['id']
    party_members = json.loads(party['data'][0]['members'])
    if str(character_id) in party_members.keys():
        return await edit_ephemeral(info_messages["player_already_in_party"], ctx)
    level = char_info['data']['level']
    accept_custom_id = PersistentCustomID(bot, "accept", [str(ctx.user.id), ctx.member.nick, character_id, package['party_id'], package['message_id'], level])  # discord_id, nick, char_id, party_id, msg_id, level, host_id
    accept_button = interactions.Button(
        style=interactions.ButtonStyle.SUCCESS,
        label="ACEITAR",
        custom_id=str(accept_custom_id)
    )

    refuse_custom_id = PersistentCustomID(bot, "refuse", [str(ctx.user.id), ctx.member.nick])
    refuse_button = interactions.Button(
        style=interactions.ButtonStyle.DANGER,
        label="RECUSAR",
        custom_id=str(refuse_custom_id)
    )
    actionrow = interactions.ActionRow(components=[accept_button, refuse_button])
    user = await interactions.get(bot, interactions.User, object_id=package['host_id'])
    user._client = bot._http
    channel = await ctx.get_channel()
    parent_channel = await interactions.get(bot, interactions.Channel, object_id=channel.parent_id)
    parent_channel._client = bot._http
    await edit_ephemeral("Convite solicitado, aguarde a resposta do dono do grupo", ctx)
    await user.send(f"{ctx.member.nick} Level: {level} quer entrar no seu grupo na missão {parent_channel.url}", components=actionrow)


@bot.persistent_component("accept")
async def manage_apply(ctx, package):
    await ctx.message.delete()
    await ctx.send("Inserindo jogador no grupo", ephemeral=True)
    host_id = queries.fetch_host_id_by_party_id(package[3])
    if str(ctx.user.id) != host_id['data']['discord_id']:
        message = "Apenas o líder do grupo pode clicar nesses botões"
        return await edit_ephemeral(message, ctx)
    # discord_id=0, nick=1, char_id=2, party_id=3, msg_id=4, level=5
    if not host_id['status']:
        return await edit_ephemeral("Ocorreu um erro", ctx)
    message = queries.insert_player_in_party(package[0], package[2], package[3])
    if not message["status"]:
        message = info_messages[message['data']]
        return await edit_ephemeral(message, ctx)
    message = f"{package[1]} foi aceito"
    await edit_ephemeral(message, ctx)
    msg = await interactions.get(bot, interactions.Message, object_id=package[4], parent_id=ctx.channel_id)
    msg._client = bot._http
    await msg.edit(msg.content+f"\n<@{package[0]}> Level: {package[5]}")


@bot.persistent_component("refuse")
async def manage_apply(ctx, package):
    await ctx.message.delete()
    await ctx.send(f"Você recusou a entrada de {package[1]} no grupo", components=None, ephemeral=True)


@bot.persistent_component("cancel_apply")
async def cancel_apply(ctx, package):
    # host_id=0 #last_message_id=1, message_id=2, party_id=3
    if ctx.user.id == package[0]:
        await ctx.send("Desfazendo o grupo", ephemeral=True)
        message = queries.disband_party(package[3])
        if not message['status']:
            return edit_ephemeral(message['data'], ctx)
        channel = await ctx.get_channel()
        msg1 = await interactions.get(bot, interactions.Message, object_id=package[1], parent_id=ctx.channel.parent_id)
        msg1._client = bot._http
        msg2 = await interactions.get(bot, interactions.Message, object_id=package[2], parent_id=ctx.channel.parent_id)
        msg2._client = bot._http
        await msg1.delete()
        await msg2.delete()
        await channel.delete()
    else:
        await ctx.send("Saindo do grupo", ephemeral=True)
        message = queries.remove_party_member(str(ctx.user.id), package[3])
        if not message['status']:
            return await edit_ephemeral(message['data'], ctx)
        channel = await ctx.get_channel()
        msg = await interactions.get(bot, interactions.Message, object_id=package[2], parent_id=channel.parent_id)
        msg._client = bot._http
        raw_list = msg.content.split("\n")
        base_message = f"{raw_list[0]}\n\n{raw_list[2]} \n\n"
        members = []
        for char in raw_list[4:]:
            if str(ctx.user.id) not in char:
                members.append(char)
        members_string = '\n'.join(members)
        final_message = base_message + members_string
        await msg.edit(final_message)
        await edit_ephemeral("Removido do grupo", ctx)


@bot.command(
    name="select_party",
    description="Escolher party que vai fazer a missão"
)
async def select_party(ctx: interactions.CommandContext):
    await ctx.send("Selecionando grupo", ephemeral=True)
    channel_id = queries.check_channel_id_owner(str(ctx.user.id))
    if not channel_id['status']:
        return await edit_ephemeral(channel_id['data'], ctx)
    if channel_id['data']['channel_id'] != str(ctx.channel_id):
            return await edit_ephemeral("Você não é o narrador desse canal", ctx)
    hosts_data = queries.fetch_group_hosts_by_channel(str(ctx.channel_id))
    if not hosts_data['status']:
        return await edit_ephemeral(hosts_data['data'], ctx)
    hosts_list = []
    for host in hosts_data['data']:
        hosts_list.append(interactions.SelectOption(label=host['name'], value=host['id']))
    select_party = interactions.SelectMenu(
        custom_id="select_party",
        options=hosts_list,
        placeholder="Selecione para qual grupo você deseja narrar",
        min_values=1,
        max_values=1,
    )
    await ctx.edit(components=select_party)

@bot.component("select_party")
async def select_party_host(ctx: interactions.ComponentContext, user=None):
    await ctx.edit("Selecionando party", components=None)
    message = queries.change_mission_active_party(str(ctx.channel_id),ctx.data.values[0])
    if not message['status']:
        return await edit_ephemeral(message['data'], ctx)
    await edit_ephemeral(message['data'], ctx)


@bot.command(
    name="generate_item",
    description="TBD",
    options=[
        interactions.Option(
            name="level",
            description="level do item",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="quant",
            description="quantidade de item",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def generate_item(ctx: interactions.CommandContext, level, quant):
    await ctx.send("Gerando item", ephemeral=True)
    list = queries.fetch_items_by_level(level)
    if not list['status']:
        return await edit_ephemeral("Erro ao gerar item", ctx)
    new_list = [x[0] for x in list['data']]
    items = random.sample(new_list, quant)
    items_string = "\n".join(items)
    await edit_ephemeral(items_string, ctx)

async def edit_ephemeral(message, ctx):
    await bot._http.edit_interaction_response(data={"content": message}, token=ctx.token,
                                              application_id=ctx.application_id)
bot.start()
