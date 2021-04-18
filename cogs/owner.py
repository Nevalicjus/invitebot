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

class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def serverinfo(self, ctx, guild: discord.Guild = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        self.log(f"{ctx.author} requested server info for {ctx.guild.name}[{ctx.guild.id}]")
        if guild == "None":
            guild = ctx.message.guild

        embed = discord.Embed(title = f"**Server {guild.name}**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url=guild.icon_url_as(format="png"))
        embed.add_field(name = "**Owner**", value = f"<@{guild.owner.id}>[`{guild.owner_id}`]", inline = False)
        embed.add_field(name = "**ID**", value = f"`{guild.id}`", inline = True)
        embed.add_field(name = "**Region**", value = guild.region, inline = True)
        if guild.premium_tier != 0:
            embed.add_field(name = "**Boost Status**", value = guild.premium_tier, inline = True)
        if guild.rules_channel != None:
            embed.add_field(name = "**Rules_Channel**", value = guild.rules_channel, inline = True)
        embed.add_field(name = "**Members**", value = guild.member_count, inline = True)
        embed.add_field(name = "**Roles**", value = len(guild.roles), inline = True)
        embed.add_field(name = "**Channels**", value = f"Categories ~ {len(guild.categories)}\nText Channels ~ {len(guild.text_channels)}\nVoice Channels ~ {len(guild.voice_channels)}", inline = True)

        if guild.splash != None:
            embed.add_field(name = "**Splash URL**", value = guild.splash_url, inline = True)
        if guild.banner != None:
            embed.add_field(name = "**Banner URL**", value = guild.banner_url, inline = True)
        if guild.description != None:
            embed.add_field(name = "**Guild Description**", value = guild.description, inline = True)
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')}  |  Protokolant made with \u2764\ufe0f by Maciej Bromirski")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.is_owner()
    async def ping(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        self.log(ctx.guild.id, f"{ctx.message.author} pinged me on {ctx.message.channel}. Latency was equal to {round(self.client.latency * 1000)}ms")
        await ctx.send(f'Pong! Latency equals {round(self.client.latency * 1000)}ms')

    @commands.command()
    @commands.is_owner()
    async def leave(self, ctx, guild: discord.Guild = "None"):
        if guild == "None":
            guild = ctx.message.guild
        self.log(guild.id, f"Leaving guild due to request by {ctx.message.author}[{ctx.message.author.id}]")

    @commands.command()
    @commands.is_owner()
    async def err(ctx):
        with open('file.txt', 'r') as f:
            file = json.load(f)

    @commands.command(help="logs x")
    @commands.is_owner()
    async def alog(self, ctx, log_entry):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        self.log(0, f"{ctx.author}[{ctx.author.id}]: {log_entry}")


    def log(self, guild_id, log_msg: str):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            logfile = config['LogFile']

        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[1;31mOWNER-UTILITIES\033[0;0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [OWNER-UTILITIES]: " + log_msg + "\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[1;31mOWNER-UTILITES\033[0;0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [OWNER-UTILITES]: " + log_msg + "\n")

    def checkPerms(self, user_id, guild_id):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            admin_roles = config['General']['AdminRoles']
        with open(f'main-config.json', 'r') as f:
            main_config = json.load(f)
            owners = main_config['OwnerUsers']

        isAble = 0

        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)

        if user_id in owners:
            isAble += 1
        if user_id == guild.owner_id:
            isAble += 1
        for role in member.roles:
            if role.id in admin_roles:
                isAble += 1

        if isAble >= 1:
            return True
        else:
            return False

    def checkInvos(self, guild_id):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            delinvos = config['General']['DeleteInvocations']

        if delinvos == 1:
            return True
        else:
            return False

    def constructResponseEmbedBase(self, desc):
        embed = discord.Embed(title = f"**InviteBot**", description = desc, color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url="https://nevalicjus.github.io/docs/invitebot.png")
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")

        return embed

    async def serverLog(self, guild_id, type, log_msg):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            log_channel_id = config['General']['ServerLog']
        if log_channel_id == 0:
            return False

        if type in ["inv_created", "inv_added", "inv_made"]:
            em_color = discord.Colour.from_rgb(67, 181, 129)
        if type in ["member_joined"]:
            em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["inv_deleted", "inv_removed"]:
            em_color = discord.Colour.from_rgb(240, 71, 71)

        embed = discord.Embed(title = f"**InviteBot Logging**", color = em_color)
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")


        if type == "inv_created":
            embed.add_field(name = "Invite Created", value = log_msg, inline = False)
        if type == "inv_added":
            embed.add_field(name = "Invite-Role Link Added", value = log_msg, inline = False)
        if type == "inv_made":
            embed.add_field(name = "Invite Made", value = log_msg, inline = False)
        if type == "member_joined":
            embed.add_field(name = "Member Joined", value = log_msg, inline = False)
        if type == "inv_deleted":
            embed.add_field(name = "Invite Deleted", value = log_msg, inline = False)
        if type == "inv_removed":
            embed.add_field(name = "Invite-Role Link Removed", value = log_msg, inline = False)

        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(embed = embed)

def setup(client):
    client.add_cog(Owner(client))
