import json
import re
import discord
import models.queries as queries
import interactions
import settings

bot = interactions.Client(
    token=settings.DISCORD_TOKEN,
    default_scope=966828980999180288,
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MEMBERS | interactions.Intents.ALL
)


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


bot.start()
