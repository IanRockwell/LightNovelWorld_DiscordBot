import discord
from discord import option
import time
from discord.ext import tasks

# Internal Imports
from auth import auth
from scraper import scraper
from data import data

max_subscriptions = 8

def run_discord_bot():
    bot = discord.Bot()

    @bot.event
    async def on_ready():
        notifications.start()
        print(f"----------------------------------\n"
              f"Successfully logged into bot account\n"
              f"\n"
              f"User: {bot.user}\n"
              f"User ID: {bot.user.id}\n"
              f"----------------------------------")

    @bot.slash_command(description="Your subscribed light novels!")
    async def subscriptions(ctx: discord.ApplicationContext):
        subscriptions = data.get_user_subscriptions(userid=str(ctx.author.id))
        if len(subscriptions) == 0:
            embed = discord.Embed(
                title=f"No Subscriptions",
                description="You are not subscribed to any light novels.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        description = "Here are the light novels you are subscribed to:\n** **"
        for novel in subscriptions:
            description = description + f"\n- {novel}"
            time.sleep(0.1)
        embed = discord.Embed(
            title=f"Subscribed Light Novels ({len(subscriptions)}/{max_subscriptions})",
            description=description,
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @bot.slash_command(description="Subscribe to a light novel!")
    @option("url",
            description="The LightNovelWorld URL of the light novel you would like to subscribe to.",
            required=True)
    async def subscribe(ctx: discord.ApplicationContext, url: str):
        novel_info = scraper.get_novel_info(url)
        if not novel_info:
            embed = discord.Embed(
                title="Invalid URL",
                description="The URL you specified is not a valid Light Novel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        subscriptions = data.get_user_subscriptions(userid=str(ctx.author.id))
        if max_subscriptions <= len(subscriptions):
            embed = discord.Embed(
                title="Maximum Reached",
                description="You are subscribed to the maximum amount of Light Novels.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if novel_info['name'] in subscriptions:
            embed = discord.Embed(
                title=novel_info['name'],
                description="You are already subscribed to this novel.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=novel_info['thumbnail_url'])
            embed.url = url
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if len(data.get_novel_subscribers(novelid=novel_info['name'])) == 0:
            chapter_number, chapter_name = scraper.get_novel_latest_chapter(url=url)
            data.add_novel(novelid=novel_info['name'], latest_chapter=chapter_number, url=url)
        data.add_novel_subscriber(novelid=novel_info['name'], userid=str(ctx.author.id))
        total_subscribers = len(data.get_novel_subscribers(novelid=novel_info['name']))

        embed = discord.Embed(
            title=novel_info['name'],
            description="You have successfully subscribed to this novel!",
            color=discord.Color.brand_green()
        )
        embed.set_thumbnail(url=novel_info['thumbnail_url'])
        embed.url = url
        embed.add_field(name="Latest Chapter", value=novel_info['latest_chapter'], inline=False)
        embed.add_field(name="Total Subscribers", value=str(total_subscribers), inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

    @bot.slash_command(description="Unsubscribe from a light novel!")
    @option("url",
            description="The LightNovelWorld URL of the light novel you would like to unsubscribe from.",
            required=True)
    async def unsubscribe(ctx: discord.ApplicationContext, url: str):
        if url == "*":
            data.unsubscribe_user_from_all_novels(str(ctx.author.id))
            embed = discord.Embed(
                title="All Novels",
                description="You have successfully unsubscribed from all novels!",
                color=discord.Color.brand_green()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        novel_info = scraper.get_novel_info(url)
        if not novel_info:
            embed = discord.Embed(
                title="Invalid URL",
                description="The URL you specified is not a valid Light Novel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if novel_info['name'] not in data.get_user_subscriptions(str(ctx.author.id)):
            embed = discord.Embed(
                title=novel_info['name'],
                description="You are not subscribed to this novel.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=novel_info['thumbnail_url'])
            embed.url = url
            await ctx.respond(embed=embed, ephemeral=True)
            return

        data.remove_novel_subscriber(novelid=novel_info['name'], userid=str(ctx.author.id))
        total_subscribers = len(data.get_novel_subscribers(novelid=novel_info['name']))

        embed = discord.Embed(
            title=novel_info['name'],
            description="You have successfully unsubscribed from this novel!",
            color=discord.Color.brand_green()
        )
        embed.set_thumbnail(url=novel_info['thumbnail_url'])
        embed.url = url
        embed.add_field(name="Total Subscribers", value=str(total_subscribers), inline=False)

        await ctx.respond(embed=embed, ephemeral=True)

    @tasks.loop(seconds=300)
    async def notifications():
        novels = data.get_novels_with_subscribers()
        current_timestamp = f"<t:{int(time.time())}:R>"
        for novel in novels:
            chapter_number, chapter_name = scraper.get_novel_latest_chapter(novel[2])
            if int(chapter_number) == int(novel[1]):
                continue
            amount_of_new_chapters = int(chapter_number) - int(novel[1])
            print(f"[bots.notifications] {novel[0]} released {amount_of_new_chapters} new chapter(s)")
            embed = discord.Embed(
                title=f"{novel[0]}",
                description=f"{current_timestamp}\n"
                            f"{novel[0]} has released new __**{amount_of_new_chapters} chapter(s)**__!\n"
                            f"** **\n"
                            f"[Link to next chapter]({novel[2]}/chapter-{int(novel[1]) + 1})\n"
                            f"** **\n"
                            f"If you want to stop recieving notifications for this series use __/unsubscribe__.\n"
                            f"** **\n",
                color=discord.Color.from_rgb(50, 205, 50))
            data.modify_novel_latest_chapter(novel[0], chapter_number)
            users = data.get_novel_subscribers(novel[0])
            print(users)
            for user in users:
                member = await bot.fetch_user(user)
                await member.send(embed=embed)

    token = auth.get_value_from_auth_json("token")
    bot.run(token)
