import json
import re
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


@bot.event
async def on_ready():
    print('ready')


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
    if not all(char.isalpha() or char.isspace() for char in name): return await ctx.send("Errou")
    message = queries.insert_user_and_character(str(ctx.author.id), name, {'lvl': '966878470305087507'})
    if not message['status']: return await ctx.send(message['data'])
    await ctx.send(message['data'], ephemeral=True)
    await ctx.author.modify(roles=[966878470305087507])
    await ctx.author.modify(nick=name)


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
    print(ctx.data.values[0])
    char = queries.fetch_character_by_id_and_insert_active_character(ctx.data.values[0])['data'][0]
    print(ctx.data.values)
    roles = json.loads(char['roles_id'])
    role_list = []
    for roleid in roles.values():
        role_list.append(int(roleid))
    await ctx.author.modify(roles=role_list)
    await ctx.author.modify(nick=char['name'])
    await ctx.send("sup nigga", ephemeral=True)


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
        return await ctx.send("invalido", ephemeral=True)
    queries.insert_hero_link(str(ctx.author.id), link)
    await ctx.send("Link cadastrado", ephemeral=True)


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
        return await ctx.send("beyond invalido", ephemeral=True)
    queries.insert_beyond_link(str(ctx.author.id), link)
    await ctx.send("Link cadastrado", ephemeral=True)


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
