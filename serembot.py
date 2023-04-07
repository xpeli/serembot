import discord
from discord.ext import commands, tasks
import datetime

#----------------------------------------------------------#
"""
    * SeremBot
    * Author: xpeli
    * Version: 1.0
    * Description: Discord bot for tracking pooping time
"""
#----------------------------------------------------------#
bot = commands.Bot(command_prefix="!")

pooping_users = {}
summary = {}
pooping_prices = {}

# Start pooping command
@bot.command()
async def start_pooping(ctx):
    user_id = ctx.author.id
    if user_id not in pooping_users:
        pooping_users[user_id] = datetime.datetime.now()
        await ctx.send(f"{ctx.author.mention} started pooping.")
    else:
        await ctx.send(f"{ctx.author.mention} you're already pooping!")

# Stop pooping command
@bot.command()
async def stop_pooping(ctx):
    user_id = ctx.author.id
    if user_id in pooping_users:
        start_time = pooping_users[user_id]
        duration = datetime.datetime.now() - start_time
        duration_in_minutes = duration.total_seconds() / 60

        if user_id not in summary:
            summary[user_id] = 0

        summary[user_id] += duration_in_minutes

        if user_id not in pooping_prices:
            pooping_prices[user_id] = 0

        pooping_prices[user_id] += (duration.total_seconds() / 3600) * 300
        del pooping_users[user_id]

        await ctx.send(f"{ctx.author.mention} stopped pooping. Total duration: {duration_in_minutes:.2f} minutes.")
    else:
        await ctx.send(f"{ctx.author.mention} you're not currently pooping!")

# Check for users who forgot to stop pooping
@tasks.loop(minutes=1)
async def check_pooping_users():
    current_time = datetime.datetime.now()
    for user_id, start_time in pooping_users.copy().items():
        duration = current_time - start_time
        if duration.total_seconds() >= 3600:  # 1 hour in seconds
            summary[user_id] += 20
            pooping_prices[user_id] += (20 / 60) * 300
            del pooping_users[user_id]

@bot.command()
async def poop_summary(ctx):
    summary_message = "Poop Summary:\n"
    total_duration = 0
    total_cost = 0

    for user_id, duration in summary.items():
        user = await bot.fetch_user(user_id)
        price = pooping_prices[user_id]
        total_duration += duration
        total_cost += price
        summary_message += f"{user.name}: {duration:.2f} minutes, {price:.2f} CZK\n"

    summary_message += f"\nTotal duration for all users: {total_duration:.2f} minutes"
    summary_message += f"\nTotal cost for all users: {total_cost:.2f} CZK"

    await ctx.send(summary_message)

# Start the check_pooping_users task
@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    check_pooping_users.start()

bot.run("YOUR_TOKEN")