import models.queries

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
    await ctx.send(nome, ephemeral=True)



bot.start()