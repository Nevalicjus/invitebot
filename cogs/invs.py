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

class Invs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)

        invites['Invites'][f"{invite.code}"] = {"roles": [], "uses": 0}

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        self.log(invite.guild.id, f'Invite {invite.code} was created')
        await self.serverLog(invite.guild.id, "inv_created", "Invite - https://discord.gg/{0} | Invite Channel - <#{1}>\nInviter - {2}\nMax Age - {3} | Max Uses - {4}".format(invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.max_uses))

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)

        del invites['Invites'][f"{invite.code}"]

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        self.log(invite.guild.id, f'Invite {invite.code} was deleted')
        await self.serverLog(invite.guild.id, "inv_deleted", "Invite - https://discord.gg/{0} | Invite Channel - <#{1}>\nInviter - {2}\nMax Age - {3} | Uses - {4}".format(invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.uses))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.add_inv_roles(await self.find_used_invite(member), member)

    async def add_inv_roles(self, invite, member):
        with open(f'configs/{member.guild.id}.json', 'r') as f:
            invites = json.load(f)

        for x in invites['Invites'][f"{invite}"]["roles"]:
            try:
                role = member.guild.get_role(x)
                await member.add_roles(role)
                self.log(invite.guild.id, f"Found invite role: {role.name} and role was added")
            except KeyError:
                self.log(invite.guild.id, f"No role for invite {invite}")

    async def find_used_invite(self, member):
        found_code = ''
        invite_list = await member.guild.invites()
        uses = {}

        with open(f'configs/{member.guild.id}.json', 'r') as f:
            invites = json.load(f)
        curr_uses = {}

        for invite in invites['Invites']:
            curr_uses[f"{invite}"] = invites['Invites'][f"{invite}"]["uses"]

        for invite in invite_list:
            uses[f"{invite.code}"] = invite.uses
            try:
                if uses[f"{invite.code}"] != curr_uses[f"{invite.code}"]:
                    self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code}")
                    await self.serverLog(member.guild.id, "member_joined", "Member <@{0}>[`{1}`] joined with invite `{2}`".format(member.id, member.id, invite.code))

                    found_code = invite.code
            except KeyError:
                with open(f'configs/{member.guild.id}.json', 'r') as f:
                    invites = json.load(f)
                if uses[f"{invite.code}"] == 0:
                    try:
                        invites['Invites'][f"{invite.code}"]["uses"] = 0
                    except KeyError:
                        invites['Invites'][f"{invite.code}"] = {"roles": [], "uses": 0}
                    self.log(invite.guild.id, f"New Invite {invite.code}")

                with open(f'configs/{member.guild.id}.json', 'w') as f:
                    json.dump(invites, f, indent = 4)

        for invite_code in uses:
            try:
                invites['Invites'][f"{invite_code}"]["uses"] = uses[f"{invite_code}"]
            except KeyError:
                try:
                    invites['Invites'][f"{invite_code}"] = {"roles": [], "uses": uses[f"{invite_code}"]}
                except KeyError:
                    invites['Invites'][f"{invite_code}"] = {"roles": [], "uses": 0}

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        return found_code


    @commands.command(aliases = ['inva'])
    async def add(self, ctx, invite: discord.Invite, role: discord.Role):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.append(role.id)
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] added role {role.name} to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_added", "{0}[`{1}`] linked role {2}[`{3}`] to {4}".format(ctx.author, ctx.author.id, role.name, role.id, invite.code))


        except KeyError:
            invites['Invites'][f"{invite.code}"] = {"roles": [role.id], "uses": 0}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to add role {role.name} to non-existent in db invite, so it was created with starting role {role.name}")

        await ctx.send(f"Added role {role.name} to invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)



    @commands.command(aliases = ['invdel', 'invrem', 'invr'])
    async def remove(self, ctx, invite: discord.Invite, role: discord.Role = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        if role != "None":
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.remove(role.id)
            invites['Invites'][f"{invite.code}"]["roles"] = inv_roles

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed link from invite {invite.code} to role {role.name}")
            await self.serverLog(ctx.guild.id, "inv_removed", "{0}[`{1}`] removed the link of role {2}[`{3}`] to {4}".format(ctx.author, ctx.author.id, role.name, role.id))

            await ctx.send(f"Removed link from invite {invite.code} to {role.name}")

        else:
            invites['Invites'][f"{invite.code}"]["roles"] = []

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed all links to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_removed", "{0}[`{1}`] removed all role links to {2}".format(ctx.author, ctx.author.id, invite.code))

            await ctx.send(f"Removed all links from invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)


    @commands.command(aliases = ['invlist', 'invls'])
    async def list(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        no_fields = 0

        embed = discord.Embed(title = f"**Invite List**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")

        for inv in invites['Invites']:
            about = ''
            for invrole in invites['Invites'][f"{inv}"]["roles"]:
                role = ctx.guild.get_role(invrole)
                about += f"{role.name}\n"
            about += f"Uses - {invites['Invites'][inv]['uses']}\n"
            if about != '':
                embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                no_fields +=1
            if no_fields == 25:
                await ctx.send(embed = embed)
                no_fields = 0
                for i in range(25):
                    embed.remove_field(0)
        if no_fields != 0:
            await ctx.send(embed = embed)


    @commands.command(aliases = ['invm'])
    async def make(self, ctx, channel: discord.TextChannel, role: discord.Role, uses: int = 0, age: int = 0):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        invite = await channel.create_invite(max_age = age, max_uses = uses)

        invites['Invites'][f"{invite.code}"] = {"roles": [role.id], "uses": 0}

        await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite in {channel} with {role} on join, age: {age} and uses: {uses}")
        self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite in {channel} with {role} on join, age: {age} and uses: {uses}")
        await self.serverLog(ctx.guild.id, "inv_made", "<@{0}>[`{1}`] created invite `https://discord.gg/{2}` in {3} with {4} on join, age: {5} and uses: {6}".format(ctx.author.id, invite.code, ctx.author.id, channel, role, invite.max_age, invite.max_uses))


        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    def log(self, guild_id, log_msg: str):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            logfile = config['LogFile']
        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[33mINVROLES\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [INVROLES]: " + log_msg + "\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[33mINVROLES\033[0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [INVROLES]: " + log_msg + "\n")

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
    client.add_cog(Invs(client))
