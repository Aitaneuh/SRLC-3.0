import discord
import aiosqlite
import random
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

@bot.command(name="queue", aliases=["q"])
async def queue(ctx):
    game_id = await get_game_by_user(ctx.author.id)

    if game_id != 0:
        await ctx.send("You are already in a queue.")
        return

    if ctx.channel.id == 1296464211680952401: #Global
        rank = "global"
    elif ctx.channel.id == 1296512459133419531: #S
        rank = "S"
    elif ctx.channel.id == 1296512468977188864: #X
        rank = "X"
    elif ctx.channel.id == 1296512479349706782: #A
        rank = "A"
    elif ctx.channel.id == 1296512487478530100: #B
        rank = "B"

    count = await count_queued_game_by_rank(rank)

    if count == 0:
        await create_game(rank)

        game_id = await get_queued_game_id_by_rank(rank)

        await add_to_queue(ctx.author.id, game_id)

        guild = ctx.guild
        start_queue_role = discord.utils.get(guild.roles, id=1296514152705036389)

        await ctx.send(f"1/6 | {ctx.author.mention} has been added to the Rank {rank} queue. {start_queue_role.mention}")
    else:
        game_id = await get_queued_game_id_by_rank(rank)

        await add_to_queue(ctx.author.id, game_id)

        player_count = await count_player_by_game(game_id)
        
        if player_count < 5:
            await ctx.send(f"{player_count}/6 | {ctx.author.mention} has been added to the Rank {rank} queue.")
        elif player_count == 5:
            guild = ctx.guild
            last_chance_role = discord.utils.get(guild.roles, id=1296514205947531344)
            await ctx.send(f"{player_count}/6 | {ctx.author.mention} has been added to the Rank {rank} queue. {last_chance_role.mention}")
        else:
            await ctx.send(f"{player_count}/6 | {ctx.author.mention} has been added to the Rank {rank} queue.")
            await start_game(game_id)

            players = await get_players_by_game(game_id)

            host_id = random.choice(players)
            await add_host_id(host_id, game_id)

            random.shuffle(players)

            team_blue = players[:3]
            for player_id in team_blue:
                await update_player_team(player_id, "blue")

            team_orange = players[3:]
            for player_id in team_orange:
                await update_player_team(player_id, "orange")

            team_blue_mentions = ", ".join([f"<@{player_id}>" for player_id in team_blue])
            team_orange_mentions = ", ".join([f"<@{player_id}>" for player_id in team_orange])
            
            await ctx.send(f"# Game {game_id} has been created\n\n## Team Blue\n\n{team_blue_mentions}\n\n## Team Orange\n\n{team_orange_mentions}")



#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="leave-queue", aliases=["l", "leave"])
async def leave_queue(ctx):
    game_id = await get_game_by_user(ctx.author.id)

    if game_id == "0":
        await ctx.send("You are not in a queue.")
        return

    if ctx.channel.id == 1296464211680952401: #Global
        rank = "global"
    elif ctx.channel.id == 1296512459133419531: #S
        rank = "S"
    elif ctx.channel.id == 1296512468977188864: #X
        rank = "X"
    elif ctx.channel.id == 1296512479349706782: #A
        rank = "A"
    elif ctx.channel.id == 1296512487478530100: #B
        rank = "B"

    count = await count_queued_game_by_rank(rank)

    if count == 1:
        await delete_game(game_id)

        await remove_from_queue(ctx.author.id)

        await ctx.send(f"The queue has been canceled")
    else:
        await remove_from_queue(ctx.author.id)

        player_count = await count_player_by_game(game_id)

        await ctx.send(f"{player_count}/6 | {ctx.author.mention} has been removed from the Rank {rank} queue.")


#-------------------------------------------------------------------------------------------------------------------------

bot.run(TOKEN)