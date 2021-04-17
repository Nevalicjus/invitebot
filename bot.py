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

client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="inv!help | https://discord.gg/wsEU32a3ke"))
    log(f"InviteBot ready")


def log(string: str):
    print(f"[{datetime.datetime.now()}] : " + string)
    with open(logfile, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] : " + string + "\n")

client.run(token)
