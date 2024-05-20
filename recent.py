import discord
from discord.ext import commands
import requests
import datetime


TOKEN = 'YOUR_BOT_TOKEN'


intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


def get_recent_anime():
    url = "https://api.jikan.moe/v4/seasons/now"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        return []


@bot.command(name='recentanime', help='Fetches the recent anime releases of the last month')
async def recent_anime(ctx):
    anime_list = get_recent_anime()
    if not anime_list:
        await ctx.send("Couldn't fetch the recent anime releases. Please try again later.")
        return

    embed = discord.Embed(
        title="Recent Anime Releases",
        description="Here are some of the recent anime releases from the last month",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.utcnow()
    )

    embed.set_thumbnail(url="https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif")  # Example GIF
    for anime in anime_list:
        title = anime['title']
        aired_from = anime['aired']['from']
        if aired_from:
            aired_from = aired_from.split('T')[0]  # Get the date only
        else:
            aired_from = 'Unknown'

        embed.add_field(
            name=title,
            value=f"Release Date: {aired_from}",
            inline=False
        )

    await ctx.send(embed=embed)


bot.run(TOKEN)
