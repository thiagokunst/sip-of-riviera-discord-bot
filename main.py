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
            name="nome",
            description="TBD",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def register(ctx:interactions.CommandContext, nome: str,):
    user_discord_id = ctx.author.id
    user_db = queries.fetch_user_by_id(user_discord_id)
    if(user_db['status']):
        if(len(user_db['data']) < 1):
            await register_user(ctx, user_discord_id)
        await register_char(ctx, user_db['data']['id'])
    else:
        await ctx.send('Deu ruim')
    print()
    await ctx.send(nome, ephemeral=True)
#aux
async def register_user(ctx, user_discord_id):
    db_user_insert = queries.insert_user(user_discord_id)
    if(db_user_insert['status']):
        ctx.send('deu bom')
    else:
        ctx.send('deu ruim')
async def register_char(ctx, user_db_id):
    queries.insert_character(user_db_id)

print(queries.fetch_user_by_id('1'))
bot.start()