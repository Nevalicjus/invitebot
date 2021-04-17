import discord
from discord.ext import commands
import datetime
import json
import os
import asyncio
intents = discord.Intents.default()
intents.members = True

class Invs(commands.Cog):
    def __init__(self, client):
        self.client = client

    with open('config.json', 'r') as f:
        config = json.load(f)
        admin_roles = config['AdminRoles']
        delinvos = config['DeleteInvocations']

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)

        invites['Invites'][f"{invite.code}"] = {"roles": [], "uses": 0}

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        self.log(invite.guild.id, f'Invite {invite.code} was created in guild {invite.guild.name}[{invite.guild.id}]')

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)

        del invites['Invites'][f"{invite.code}"]

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        self.log(invite.guild.id, f'Invite {invite.code} was deleted in guild {invite.guild.name}[{invite.guild.id}]')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.add_inv_roles(await self.find_used_invite(member), member)

    async def add_inv_roles(self, invite, member):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
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

        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)
        curr_uses = {}

        for invite in invites:
            curr_uses[f"{invite}"] = invites['Invites'][f"{invite}"]["uses"]

        for invite in invite_list:
            uses[f"{invite.code}"] = invite.uses
            try:
                if uses[f"{invite.code}"] != curr_uses[f"{invite.code}"]:
                    self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code}")
                    found_code = invite.code
            except KeyError:
                with open(f'configs/{invite.guild.id}.json', 'r') as f:
                    invites = json.load(f)
                if uses[f"{invite.code}"] == 0:
                    try:
                        invites['Invites'][f"{invite.code}"]["uses"] = 0
                    except KeyError:
                        invites['Invites'][f"{invite.code}"] = {"roles": [], "uses": 0}
                    self.log(invite.guild.id, f"New Invite {invite.code}")

                with open(f'configs/{invite.guild.id}.json', 'w') as f:
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
    async def invadd(self, ctx, invite: discord.Invite, role: discord.Role):
        if checkInvos(ctx.guild.id) = 1:
            await ctx.message.delete(delay=3)

        if checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.append(role.id)
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] added role {role.name} to invite {invite.code}")

        except KeyError:
            invites['Invites'][f"{invite.code}"] = {"roles": [role.id], "uses": 0}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to add role {role.name} to non-existent in db invite, so it was created with starting role {role.name}")

        await ctx.send(f"Added role {role.name} to invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)



    @commands.command(aliases = ['invdel', 'invrem', 'invr'])
    async def invremove(self, ctx, invite: discord.Invite, role: discord.Role = "None"):
        if checkInvos(ctx.guild.id) = 1:
            await ctx.message.delete(delay=3)

        if checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        if role != "None":
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.remove(role.id)
            invites['Invites'][f"{invite.code}"]["roles"] = inv_roles

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed link from invite {invite.code} to role {role.name}")
            await ctx.send(f"Removed link from invite {invite.code} to {role.name}")

        else:
            invites['Invites'][f"{invite.code}"]["roles"] = []

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed all links to invite {invite.code}")
            await ctx.send(f"Removed all links from invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)


    @commands.command(aliases = ['invlist', 'invls'])
    async def listinvs(self, ctx):
        if checkInvos(ctx.guild.id) = 1:
            await ctx.message.delete(delay=3)

        if checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        no_fields = 0

        embed = discord.Embed(title = f"**Invite List**", color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
        now = datetime.datetime.now()
        embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")

        for inv in invites:
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
    async def invmake(self, ctx, channel: discord.TextChannel, role: discord.Role, uses: int = 0, age: int = 0):
        if checkInvos(ctx.guild.id) = 1:
            await ctx.message.delete(delay=3)

        if checkPerms(ctx.author.id, ctx.guild.id) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        invite = await channel.create_invite(max_age = age, max_uses = uses)

        invites['Invite'][f"{invite.code}"] = {"roles": [role.id], "uses": 0}

        await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite in {channel} with {role} on join, age: {age} and uses: {uses}")
        self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite in {channel} with {role} on join, age: {age} and uses: {uses}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)


    def log(self, guild_id, log_msg: str):
        print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[33mINVROLES\033[0m]: " + log_msg)
        with open('log.txt', 'a') as f:
            f.write(f"[{datetime.datetime.now()}] : " + log_msg + "\n")

    def checkPerms(self, user_id, guild_id):
        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            config = json.load(f)
            admin_roles = config['General']['AdminRoles']
        with open(f'config.json', 'r') as f:
            main_config = json.load(f)
            owners = main_config['OwnerUsers']

        isAble = 0

        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)

        if user_id in owners:
            isAble += 1
        if user_id == guild.owner_id:
            isAble += 1
        for role in cmember.roles:
            if role.id in admin_roles:
                isAble += 1

        if isAble >= 1:
            return True
        else:
            return False

    def checkInvos(self, guild_id):
        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
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

def setup(client):
    client.add_cog(Invs(client))
