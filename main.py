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
    # Connexion à la base de données
    bot.db = await aiosqlite.connect('Main.db')

    # Création de la table si elle n'existe pas
    await create_tables()

    print("Bot is online ! ", "| Name :", bot.user.name, "| ID :", bot.user.id)
    print("//////////////////////////////////")
    try:
        synced = await bot.tree.sync()
        synced_names = [command.name for command in synced]  # Récupère les noms des commandes synchronisées
        print(f"{len(synced)} commands have been synced : {', '.join(synced_names)}")
    except Exception as e:
        print(e)

#-------------------------------------------------------------------------------------------------------------------------

@bot.event
async def on_member_join(member):
    # Récupérer le serveur (guild) où le membre a rejoint
    guild = member.guild
    
    # Récupérer le rôle que vous souhaitez attribuer au membre
    role = discord.utils.get(guild.roles, id=1296237890329776129)

    # Vérifier si le rôle existe et si le membre n'a pas déjà ce rôle
    if role is not None and role not in member.roles:
        # Ajouter le rôle au membre
        await member.add_roles(role)