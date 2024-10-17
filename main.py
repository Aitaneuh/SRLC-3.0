import discord
import aiosqlite
import schedule
import asyncio
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
from database import *


#-------------------------------------------------------------------------------------------------------------------------

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#-------------------------------------------------------------------------------------------------------------------------

activity = discord.Game(name="SRLC")
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), activity=activity, status=discord.Status.online)

#-------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_ready():

    bot.db = await aiosqlite.connect('Main.db')


    await create_tables()

    print("Bot is online ! ", "| Name :", bot.user.name, "| ID :", bot.user.id)
    print("//////////////////////////////////")
    try:
        synced = await bot.tree.sync()
        synced_names = [command.name for command in synced]  
        print(f"{len(synced)} commands have been synced : {', '.join(synced_names)}")
    except Exception as e:
        print(e)

#-------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_member_join(member):

    guild = member.guild
    

    role = discord.utils.get(guild.roles, id=1296237890329776129)

    if role is not None and role not in member.roles:

        await member.add_roles(role)

#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="set-rank")
async def set_rank(ctx, member: discord.Member, rank: str):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not an admin, so you can't use this command.")
        return

    if member is None or rank is None:
        await ctx.send("Usage : `!set-rank @User Rank`")
        return
    
    guild = ctx.guild
    if guild.get_member(member.id) is None:
        await ctx.send(f"The user {member.mention} is not found in this server.")
        return
    
    if rank not in ["S", "X", "A", "B"]:
        await ctx.send("Rank is not correct, possible ranks are : **S**, **X**, **A**, **B**")
        return
    
    if rank == "S":
        elo = 2000
    elif rank == "X":
        elo = 1600
    elif rank == "A":
        elo = 1200
    elif rank == "B":
        elo = 800

    discord_id = str(member.id)

    role_name = rank
    role = discord.utils.get(guild.roles, name=role_name)
    player_role = discord.utils.get(guild.roles, id=1296463921783509036)

    if role is not None:
        rank_roles = ["S", "X", "A", "B"]
        member_roles = [r for r in member.roles if r.name in rank_roles]
        await member.remove_roles(*member_roles)

        await member.add_roles(role)
        await member.add_roles(player_role)
    else:
        await ctx.send(f"The role '{role_name}' does not exist in this server.")


    user = await get_user(discord_id)

    if user is not None:
        await update_user(discord_id, elo, rank)
        await ctx.send(f"Rank of {member.mention} was updated to **{rank}** with an elo of **{elo}**.")
    else:
        await create_user(discord_id, elo, rank)
        await ctx.send(f"Rank of {member.mention} was set to **{rank}** with an elo of **{elo}**.")

#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="stats")
async def stats(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user = await get_user(str(member.id))

    if user is not None:
        elo = user[1]
        rank = user[2]
        wins = user[3]
        losses = user[4]
        if (losses == 0 and wins > 0):
            wl = round(wins / (losses + 1), 5)
            wg= round(wins / (wins + losses), 5)
        elif (losses == 0 and wins == 0):
            wl = "No game played"
            wg = "No game played"
        else:
            wl = round(wins / losses, 5)
            wg = round(wins / (wins + losses), 5)
        await ctx.send(f"**{member.display_name}** has an ELO of **{elo}** and a rank of **{rank}**. He has **{wins}** wins and **{losses}** losses for a W/G of **{wg}** and a W/L of **{wl}**")
    else:
        await ctx.send(f"No stats found for **{member.display_name}**.")


#-------------------------------------------------------------------------------------------------------------------------


bot.run(TOKEN)