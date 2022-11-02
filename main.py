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
    if not name.isalpha():
        return await ctx.send("Errou")
    user_discord_id = ctx.author.id
    message = queries.insert_user_and_character(str(user_discord_id), name)['data']
    await ctx.send(message, ephemeral=True)
    
bot.start()