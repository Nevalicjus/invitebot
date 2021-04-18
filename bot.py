import discord
import os
from discord.ext import commands
import json
import asyncio
import datetime
import traceback
import sys
intents = discord.Intents.default()
intents.members = True

with open('main-config.json', 'r') as f:
    config = json.load(f)
    prefix = config['Prefix']
    token = config['DiscordToken']
    logfile = config['LogFile']
    delinvos = config['DeleteOwnerCommandsInvos']

client = commands.Bot(command_prefix=prefix, intents=intents)
client.remove_command('help')

@client.event
async def on_ready():
    log("InviteBot started")
    client.loop.create_task(status_task())
    log("Status service started")
    log(f"InviteBot ready")

@client.event
async def on_command_error(ctx, exception):
    with open('main-config.json', 'r') as f:
        config = json.load(f)
        owners = config['OwnerUsers']
    log(f"There was an error that happened in {ctx.guild.name}[{ctx.guild.id}]\n caused by {ctx.message.content}, which was run by {ctx.author.name}[{ctx.author.id}]:\n")
    traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
    print("\n")
    for owner in owners:
        recipient = client.get_user(owner)
        await recipient.send(f"There was an error that happened in {ctx.guild.name}[{ctx.guild.id}] caused by {ctx.message.content}, which was run by {ctx.author.name}[{ctx.author.id}]:\n {exception}")

@client.command(help="Loads a cog.")
@commands.is_owner()
async def load(ctx, extension):
    try:
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} was loaded')
        log(f'{extension} was loaded')
    except ExtensionNotLoaded:
        await ctx.send(f'There was a problem loading {extension}')
        log(f'There was a problem loading {extension}')

@client.command()
@commands.is_owner()
async def err(ctx):
    with open('file.txt', 'r') as f:
        file = json.load(f)

    #deleting invo
    if delinvos == True:
        await ctx.message.delete(delay=5)


@client.command(help="Unloads a cog.")
@commands.is_owner()
async def unload(ctx, extension):
    try:
        client.unload_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} was unloaded')
        log(f'{extension} was unloaded')
    except ExtensionNotLoaded:
        await ctx.send(f'There was a problem unloading {extension}')
        log(f'There was a problem unloading {extension}')

    #deleting invo
    if delinvos == True:
        await ctx.message.delete(delay=5)

@client.command(help="Reloads a cog")
@commands.is_owner()
async def reload(ctx, extension):
    if extension == "all":
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                client.unload_extension(f'cogs.{filename[:-3]}')
                client.load_extension(f'cogs.{filename[:-3]}')
                await ctx.send(f'{filename[:-3]} was reloaded')
                log(f'{filename[:-3]} was reloaded')
    else:
        client.unload_extension(f'cogs.{extension}')
        client.load_extension(f'cogs.{extension}')
        await ctx.send(f'{extension} was reloaded')
        log(f'{extension} was reloaded')
    #deleting invo
    if delinvos == 1:
        await ctx.message.delete(delay=5)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

def log(log_msg: str):
    print(f"[{datetime.datetime.now()}] [\033[1;31mINTERNAL\033[0;0m]: " + log_msg)
    with open('log.txt', 'a') as f:
        f.write(f"[{datetime.datetime.now()}] [INTERNAL]: " + log_msg + "\n")

async def status_task():
    while True:
        members = 0
        for guild in client.guilds:
            members += guild.member_count
        await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name=f"on {len(client.guilds)} guilds with {members} members total"))
        await asyncio.sleep(20)
        await client.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.playing, name="inv!help | https://discord.gg/wsEU32a3ke"))
        await asyncio.sleep(20)


client.run(token)
