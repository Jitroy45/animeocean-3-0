import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
from discord_slash.model import ButtonStyle
import aiohttp
import random

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = 'YOUR_BOT_TOKEN'

intents = discord.Intents.default()
bot = Bot(command_prefix="!", intents=intents)
slash = SlashCommand(bot, sync_commands=True)

# Fetch a random anime from Jikan API
async def fetch_random_anime():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.jikan.moe/v4/anime') as resp:
            if resp.status == 200:
                data = await resp.json()
                animes = data['data']
                anime = random.choice(animes)
                return anime
            else:
                return None

@slash.slash(
    name="randomanime",
    description="Get a random anime series or movie",
)
async def _randomanime(ctx: SlashContext):
    anime = await fetch_random_anime()
    if anime:
        embed = discord.Embed(
            title=anime['title'],
            url=anime['url'],
            description=anime['synopsis'],
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=anime['images']['jpg']['image_url'])
        embed.add_field(name="Type", value=anime['type'], inline=True)
        embed.add_field(name="Episodes", value=anime['episodes'], inline=True)
        embed.add_field(name="Rating", value=anime['score'], inline=True)
        embed.add_field(name="Aired", value=anime['aired']['string'], inline=True)
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        
        buttons = [
            create_button(style=ButtonStyle.green, label="Another Anime", custom_id="another_anime")
        ]
        action_row = create_actionrow(*buttons)

        message = await ctx.send(embed=embed, components=[action_row])

        while True:
            try:
                button_ctx: ComponentContext = await wait_for_component(bot, components=action_row, timeout=60.0)
                if button_ctx.custom_id == "another_anime":
                    new_anime = await fetch_random_anime()
                    new_embed = discord.Embed(
                        title=new_anime['title'],
                        url=new_anime['url'],
                        description=new_anime['synopsis'],
                        color=discord.Color.blue()
                    )
                    new_embed.set_thumbnail(url=new_anime['images']['jpg']['image_url'])
                    new_embed.add_field(name="Type", value=new_anime['type'], inline=True)
                    new_embed.add_field(name="Episodes", value=new_anime['episodes'], inline=True)
                    new_embed.add_field(name="Rating", value=new_anime['score'], inline=True)
                    new_embed.add_field(name="Aired", value=new_anime['aired']['string'], inline=True)
                    new_embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
                    
                    await button_ctx.edit_origin(embed=new_embed)
            except:
                break
    else:
        await ctx.send("Could not fetch anime data at the moment. Please try again later.")

bot.run(BOT_TOKEN)
