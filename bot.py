import os
import json
import asyncio
import datetime

import discord
from discord.ext import commands

with open("main-config.json", "r") as mc:
    config = json.load(mc)
    token = config["DiscordToken"]
    logFile = config["LogFile"]
    delinvos = config["DeleteOwnerCommandsInvos"]

def get_prefix(cl, message):
    try:
        with open(f"configs/{message.guild.id}.json", "r") as gc:
            guild_config = json.load(gc)
            prefix = guild_config["General"]["Prefix"]
    except:
        prefix = config["Prefix"]

    return prefix

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = get_prefix, intents = intents)
client.remove_command("help")

@client.event
async def on_ready():
    ascii_art = """
  _   _              _____            _           _
 | \ | |            |_   _|          | |         | |
 |  \| | _____   __   | |  _ ____   _| |__   ___ | |_
 | . ` |/ _ \ \ / /   | | | '_ \ \ / / '_ \ / _ \| __|
 | |\  |  __/\ V /   _| |_| | | \ V /| |_) | (_) | |_
 |_| \_|\___| \_/   |_____|_| |_|\_/ |_.__/ \___/ \__|

    """
    print(f"\033[34m{ascii_art}\033[0m\nThanks for using my bot! If you like it, consider supporting me on kofi - https://ko-fi.com/nevalicjus")
    log("Invitebot started")
    loaded_cogs = await loadall()
    log(f"Cogs named: {loaded_cogs} were loaded")
    client.loop.create_task(status_task())
    log("Status service started")
    log("Invitebot ready")

@client.command()
@commands.is_owner()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} was loaded")
    log(f"{extension} was loaded")

@client.command()
@commands.is_owner()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} was unloaded")
    log(f"{extension} was unloaded")

@client.command()
@commands.is_owner()
async def reload(ctx, extension):
    if extension == "all":
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                client.unload_extension(f"cogs.{filename[:-3]}")
                client.load_extension(f"cogs.{filename[:-3]}")
                await ctx.send(f"{filename[:-3]} was reloaded")
                log(f"{filename[:-3]} was reloaded")
    else:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} was reloaded")
        log(f"{extension} was reloaded")

async def loadall():
    loaded_cogs = ""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")
            loaded_cogs += f"{filename[:-3]} "
    return loaded_cogs[:-1]

def log(log_msg: str):
    print(f"[{datetime.datetime.now()}] [\033[1;31mINTERNAL\033[0;0m]: {log_msg}")
    with open(f"{logFile}", "a") as lf:
        lf.write(f"[{datetime.datetime.now()}] [INTERNAL]: {log_msg}\n")

async def status_task():
    while True:
        members = 0
        try:
            for guild in client.guilds:
                members += guild.member_count
            await client.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.playing, name = f"on {len(client.guilds)} guilds with {members} members"))
            await asyncio.sleep(30)
            await client.change_presence(status = discord.Status.online, activity = discord.Activity(type = discord.ActivityType.playing, name = "i!help | https://invitebot.xyz"))
            await asyncio.sleep(30)
        except:
            pass


client.run(token)
