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

@client.event
async def on_ready():
    log(f"InviteBot ready")

@client.event
async def on_member_join(member):
    await add_inv_roles(await find_used_invite(member), member)


async def add_inv_roles(invite, member):
    with open(invfile, 'r') as f:
        inv_roles = json.load(f)
    try:
        for x in inv_roles[invite]:
            try:
                role = discord.utils.get(member.guild.roles, name=inv_roles[invite][x])
                log(f'Found invite role: {inv_roles[invite][x]}')
                await member.add_roles(role)
                log(f'Role added')
            except KeyError:
                log(f'No role for invite {invite}')
    except KeyError:
        return

async def find_used_invite(member):
    found_code = ''
    invite_list = await member.guild.invites()
    uses = {}
    curr_uses = await get_current_invite_uses()

    for invite in invite_list:
        uses[invite.code] = invite.uses
        try:
            if uses[invite.code] != curr_uses[invite.code]:
                log(f'User {member.name} joined with invite {invite.code}')
                found_code = invite.code
        except KeyError:
            if uses[invite.code] == 0:
                log(f'New invite: {invite.code}')
                continue
            else:
                log(f'User {member.name} joined with new invite: {invite.code}')
                found_code = invite.code

    with open(usesfile, 'w') as f:
        json.dump(uses, f)

    return found_code


async def get_current_invite_uses():
    try:
        with open(usesfile, 'r') as f:
            curr_uses = json.load(f)
    except FileNotFoundError:
        curr_uses = {}
    return curr_uses

@client.command(help="Adds a role to an invite-key in dictionary (!add role invite)")
@commands.has_permissions(administrator=True)
async def add(ctx, role: discord.Role, invite: discord.Invite):
    with open('dbs/invites.json', 'r') as f:
        inv_roles = json.load(f)

    try:
        length = len(inv_roles[f"{invite.code}"])
        inv_roles[f"{invite.code}"][f"role{length + 1}"] = f"{role.name}"
        log(f'Added role {role.name} to invite {invite.code}')

    except KeyError:
        inv_roles[f"{invite.code}"] = {}
        inv_roles[f"{invite.code}"]["role1"] = f"{role.name}"
        log(f'Added invite {invite.code} with a starting role {role.name}')

    with open('dbs/invites.json', 'w') as f:
        json.dump(inv_roles, f)

    await ctx.message.delete(delay=5)

@client.command(help="Removes an invite-key from dictionary (!remove invite)")
@commands.has_permissions(administrator=True)
async def remove(ctx, invite: discord.Invite):
    with open('dbs/invites.json', 'r') as f:
        inv_roles = json.load(f)

    del inv_roles[invite.code]

    with open('dbs/invites.json', 'w') as f:
        json.dump(inv_roles, f)
    log(f'Deleted {invite.code} invite')

    await ctx.message.delete(delay=5)

@client.command(help="Shows the invites with connected roles. Only first 25 tho")
@commands.has_permissions(administrator=True)
async def listinvs(ctx):
    with open('dbs/invites.json', 'r') as f:
        inv_roles = json.load(f)

    embed = discord.Embed(title = f"**Invite List**", color = discord.Colour.from_rgb(119, 137, 218))
    embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
    for inv in inv_roles:
        about = ''
        for invrole in inv_roles[inv]:
            about += inv_roles[inv][invrole]
            about += "\n"
        embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)

    await ctx.message.delete(delay=5)


def log(string: str):
    print(f"[{datetime.datetime.now()}] : " + string)
    with open(logfile, 'a') as f:
        f.write(f"[{datetime.datetime.now()}] : " + string + "\n")

client.run(token)
