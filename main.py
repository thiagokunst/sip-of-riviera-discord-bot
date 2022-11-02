import models.queries as queries

import interactions

import settings

bot = interactions.Client(
    token=settings.DISCORD_TOKEN,
    default_scope=966828980999180288
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
async def register(ctx:interactions.CommandContext, name: str,):
    if not name.isalpha(): return await ctx.send("Errou")
    message = queries.insert_user_and_character(str(ctx.author.id), name)['data']
    await ctx.send(message, ephemeral=True)

@bot.command(
    name="charselect",
    description="TBD",
)
async def charselect(ctx: interactions.CommandContext):
    char_list = []
    db_char_list = queries.fetch_all_characters_by_id(str(ctx.author.id))['data']
    for char in db_char_list:
        char_list.append(interactions.SelectOption(label=char['name'], value=str(char['id'])+","+char['name']))
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
    txt = ctx.data.values[0]
    splittxt = txt.split(",")
    await ctx.author.modify(nick=splittxt[1])



print(queries.fetch_all_characters_by_id("276154831033597952"))
bot.start()