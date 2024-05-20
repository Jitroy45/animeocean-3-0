import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import ButtonStyle
from discord_slash.utils import manage_components
import requests


bot = commands.Bot(command_prefix="!")
slash = SlashCommand(bot, sync_commands=True)


JIKAN_API_URL = "https://api.jikan.moe/v4"


def get_recent_anime():
    response = requests.get(f"{JIKAN_API_URL}/season/later")
    if response.status_code == 200:
        return response.json().get("anime", [])
    return []


def create_anime_embed(anime):
    embed = discord.Embed(
        title=anime["title"],
        url=anime["url"],
        description=anime["synopsis"],
        color=discord.Color.blue()
    )
    embed.set_image(url=anime["image_url"])
    embed.add_field(name="Episodes", value=anime["episodes"])
    embed.add_field(name="Airing", value=anime["airing_start"])
    embed.set_footer(text="Data provided by Jikan API")
    return embed


@slash.slash(
    name="recentanime",
    description="Show recent anime releases",
    options=[
        create_option(
            name="page",
            description="Page number",
            option_type=4,  # Integer type
            required=False
        )
    ]
)
async def recentanime(ctx: SlashContext, page: int = 1):
    anime_list = get_recent_anime()
    if not anime_list:
        await ctx.send(content="Could not fetch recent anime releases.")
        return

    items_per_page = 5
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    total_pages = (len(anime_list) + items_per_page - 1) // items_per_page

    embeds = [create_anime_embed(anime) for anime in anime_list[start_index:end_index]]
    buttons = [
        manage_components.create_button(
            style=ButtonStyle.primary,
            label="Previous",
            custom_id="previous"
        ),
        manage_components.create_button(
            style=ButtonStyle.primary,
            label="Next",
            custom_id="next"
        )
    ]
    action_row = manage_components.create_actionrow(*buttons)

    msg = await ctx.send(embed=embeds[0], components=[action_row])

    
    def check(m):
        return m.message.id == msg.id

    current_page = page

    while True:
        button_ctx = await manage_components.wait_for_component(bot, components=action_row, check=check)

        if button_ctx.custom_id == "previous" and current_page > 1:
            current_page -= 1
        elif button_ctx.custom_id == "next" and current_page < total_pages:
            current_page += 1

        start_index = (current_page - 1) * items_per_page
        end_index = start_index + items_per_page
        new_embeds = [create_anime_embed(anime) for anime in anime_list[start_index:end_index]]

        await button_ctx.edit_origin(embed=new_embeds[0])


bot.run("YOUR_DISCORD_BOT_TOKEN")
