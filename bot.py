import discord
import os
from discord.ext import commands
import json
import datetime
intents = discord.Intents.default()
intents.members = True

with open('config.json', 'r') as f:
    config = json.load(f)
    prefix = config['Prefix']
    token = config['DiscordToken']
    logfile = config['LogFile']
    invfile = config['InvitesFile']
    usesfile = config['UsesFile']

client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    log(f"InviteBot ready")


def log(string: str):
    print(f"[{datetime.datetime.now()}] : " + string)
    with open(logfile, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] : " + string + "\n")

client.run(token)
