import discord
import aiosqlite
import random
import schedule
import asyncio
from discord.ext import commands
from discord import app_commands
from discord.utils import *
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

#-------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_member_join(member):

    guild = member.guild

    role = discord.utils.get(guild.roles, id=1296237890329776129)

    if role is not None and role not in member.roles:

        await member.add_roles(role)

#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="set-rank")
async def set_rank(ctx, member: discord.Member = None, rank: str = None):

    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not an admin, only them can use this command.")
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
            
            await ctx.send(f"# Game {game_id} has been created\n\n## Team Blue\n\n{team_blue_mentions}\n\n## Team Orange\n\n{team_orange_mentions}\n\n# You can now wait until every one is here in the Lobby #{game_id}")

            guild = ctx.guild
            category = ctx.channel.category

            lobby_channel = await guild.create_voice_channel(
                name=f"Lobby #{game_id}", 
                category=category
            )
            team_blue_channel = await guild.create_voice_channel(
                name=f"Team Blue #{game_id}", 
                category=category
            )

            team_orange_channel = await guild.create_voice_channel(
                name=f"Team Orange #{game_id}", 
                category=category
            )

            overwrite_deny = discord.PermissionOverwrite()
            overwrite_deny.connect = False 

            overwrite_allow = discord.PermissionOverwrite()
            overwrite_allow.connect = True 

            await lobby_channel.set_permissions(guild.default_role, overwrite=overwrite_deny)
            for player in players:
                user = guild.get_member(player.id)
                await lobby_channel.set_permissions(user, overwrite=overwrite_allow)

            await team_blue_channel.set_permissions(guild.default_role, overwrite=overwrite_deny)
            for member in team_blue:
                user = guild.get_member(member.id)
                await team_blue_channel.set_permissions(user, overwrite=overwrite_allow)

            await team_orange_channel.set_permissions(guild.default_role, overwrite=overwrite_deny)
            for member in team_orange:
                user = guild.get_member(member.id)
                await team_orange_channel.set_permissions(user, overwrite=overwrite_allow)


#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="leave-queue", aliases=["l", "leave"])
async def leave_queue(ctx):
    game_id = await get_game_by_user(ctx.author.id)

    if game_id == "0":
        await ctx.send("You are not in a queue.")
        return
    
    user = await get_user(ctx.author.id)

    if user[5] == "ingame":
        await ctx.send("You can't leave a started game.")
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

    count = await count_player_by_game(game_id)

    if count == 1:
        await delete_game(game_id)

        await remove_from_queue(ctx.author.id)

        await ctx.send(f"The queue has been canceled")
    else:
        await remove_from_queue(ctx.author.id)

        player_count = await count_player_by_game(game_id)

        await ctx.send(f"{player_count}/6 | {ctx.author.mention} has been removed from the Rank {rank} queue.")

#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="queue-status", aliases=["status", "s"])
async def queue_status(ctx):

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

    game_id = await get_queued_game_id_by_rank(rank)

    count = await count_player_by_game(game_id)

    if count == 0:
        await ctx.send(f"# The queue for rank {rank} is empty")
        return

    player_ids = await get_players_by_game(game_id)

    player_names = []

    for player_id in player_ids:
        user = await bot.fetch_user(player_id)
        player_names.append(user.display_name)

    player_list = (", ".join(player_names))

    await ctx.send(f"# Players currently in queue for rank {rank}\n\n{player_list}")

#-------------------------------------------------------------------------------------------------------------------------
 
import discord
from discord.ext import commands
from discord.ui import View, Button

class ConfirmReportView(View):
    def __init__(self, ctx, host_id, game_id, win_color, blue_player_ids, orange_player_ids):
        super().__init__()
        self.ctx = ctx
        self.host_id = host_id
        self.game_id = game_id
        self.win_color = win_color
        self.blue_player_ids = blue_player_ids
        self.orange_player_ids = orange_player_ids

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.host_id and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to confirm the result.", ephemeral=True)
            return

        await interaction.response.send_message(f"Game #{self.game_id} reported as {self.win_color} team winning!", ephemeral=False)

        await self.report_game_results()

        self.disable_all_items()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"Game #{self.game_id} report cancelled.", ephemeral=False)

        self.disable_all_items()
        await interaction.message.edit(view=self)

    async def report_game_results(self):
        winning_team_ids = self.blue_player_ids if self.win_color == "blue" else self.orange_player_ids
        losing_team_ids = self.orange_player_ids if self.win_color == "blue" else self.blue_player_ids

        for player_id in winning_team_ids:
            await add_a_win(player_id)

        for player_id in losing_team_ids:
            await add_a_lose(player_id)

        rank = await get_rank_by_game_id(self.game_id)

        if rank != "global":
            await calculate_new_elo(winning_team_ids, losing_team_ids)

        player_ids = await get_players_by_game(self.game_id)

        for player_id in player_ids:
            await check_rank_change(self.ctx, player_id)
            await leave_a_game(player_id)

        await delete_game(self.game_id)

        await self.ctx.send(f"the game #{self.game_id} has been successfully reported. {self.win_color} has won.")


@bot.command(name="report-score", aliases=["report", "r"])
async def report_score(ctx, member: discord.Member = None, win_color: str = None):
    guild = ctx.guild

    if member is not None and not ctx.author.guild_permissions.administrator:
        await ctx.send("Only admins can report another person's game.")
        return

    if member is None:
        member = ctx.author

    game_id = await get_game_by_user(member.id)

    if game_id == "0":
        await ctx.send("You are not in a game.")
        return

    host_id = await get_host_id_by_game_id(game_id)

    if host_id is None:
        await ctx.send("You are not in a game.")
        return

    if ctx.author.id != int(host_id):
        await ctx.send("Only the host can report the result.")
        return

    blue_player_ids = await get_blue_team_players_by_game_id(game_id)
    orange_player_ids = await get_orange_team_players_by_game_id(game_id)

    if win_color not in ["blue", "orange"]:
        await ctx.send("The team entered has to be `blue` or `orange`.")
        return

    view = ConfirmReportView(ctx, host_id, game_id, win_color, blue_player_ids, orange_player_ids)
    await ctx.send(f"{ctx.author.mention}, you reported that {win_color} team won the game. do you confirm ?", view=view)



async def calculate_new_elo(winning_team_ids, losing_team_ids):

    winning_elo = []
    losing_elo = []

    k_factor = 30

    for player_id in winning_team_ids:
        elo = await get_player_elo(player_id)  
        winning_elo.append((player_id, elo))

    for player_id in losing_team_ids:
        elo = await get_player_elo(player_id) 
        losing_elo.append((player_id, elo))

    
    for player_id, old_elo in winning_elo:
        expected_score = 1 / (1 + 10 ** ((sum(losing[1] for losing in losing_elo) / len(losing_elo) - old_elo) / 400))
        new_elo = old_elo + k_factor * (1 - expected_score)
        await update_player_elo(player_id, new_elo) 

    
    for player_id, old_elo in losing_elo:
        expected_score = 1 / (1 + 10 ** ((sum(winning[1] for winning in winning_elo) / len(winning_elo) - old_elo) / 400))
        new_elo = old_elo + k_factor * (0 - expected_score)
        await update_player_elo(player_id, new_elo)


async def check_rank_change(ctx, player_id):

    guild = ctx.guild

    player_elo = await get_player_elo(player_id)

    if player_elo > 1800:
        rank = "S"
    elif player_elo < 1800 and player_elo > 1400:
        rank = "X"
    elif player_elo < 1400 and player_elo > 1000:
        rank = "A"
    elif player_elo < 1000:
        rank = "B"

    await update_user(player_id, player_elo, rank)

    member = guild.get_member(player_id)

    roles = {
        "S": discord.utils.get(guild.roles, id=1296472639577264158),
        "X": discord.utils.get(guild.roles, id=1296472715997352008),
        "A": discord.utils.get(guild.roles, id=1296472764273917952),
        "B": discord.utils.get(guild.roles, id=1296473344757207112)
    }

    correct_role = roles[rank]

    for role in roles.items():
        if role in member.roles and role != correct_role:
            await member.remove_roles(role)

    if correct_role not in member.roles:
        await member.add_roles(correct_role)

#-------------------------------------------------------------------------------------------------------------------------

@bot.command(name="clear-queue", aliases=["clear", "c"])
async def clear_queue(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not an admin, only them can use this command.")
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

    game_id = await get_queued_game_id_by_rank(rank)

    player_ids = await get_players_by_game(game_id)

    for player_id in player_ids:
        await leave_a_game(player_id)

    await delete_game(game_id)

    await ctx.send(f"Game #{game_id} has been successfuly cleared.")



#-------------------------------------------------------------------------------------------------------------------------




bot.run(TOKEN)