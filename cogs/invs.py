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

        if invite.max_uses == 1:
            invites['Invites'][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {"1use": True}}
        else:
            invites['Invites'][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {}}

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        self.log(invite.guild.id, f'Invite {invite.code} was created')
        await self.serverLog(invite.guild.id, "inv_created", "Invite - https://discord.gg/{0} | Invite Channel - <#{1}>\nInviter - {2}\nMax Age - {3} | Max Uses - {4}".format(invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.max_uses))

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        with open(f'configs/{invite.guild.id}.json', 'r') as f:
            invites = json.load(f)

        # if invite is a 1use, marked it as used so addinvroles can read roles and then delete the inv
        if "1use" in list(invites['Invites'][f"{invite.code}"]["tags"].keys()):
            if invites['Invites'][f"{invite.code}"]["tags"]["1use"] == True:
                invites['Invites'][f"{invite.code}"]["tags"]["1use"] = "used"

                inv_name = invites['Invites'][invite.code]['name']
                if inv_name != "None":
                    self.log(invite.guild.id, f"Invite {inv_name} - {invite.code} marked as 1use was deleted")
                    await self.serverLog(invite.guild.id, "inv_deleted", "Invite {0} - https://discord.gg/{1} | Invite Channel - <#{2}>\nInviter - {3}\nMax Age - {4} | Uses - {5}".format(inv_name, invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.uses))
                else:
                    self.log(invite.guild.id, f'Invite {invite.code} marked as 1use was deleted')
                    await self.serverLog(invite.guild.id, "inv_deleted", "Invite - https://discord.gg/{0} | Invite Channel - <#{1}>\nInviter - {2}\nMax Age - {3} | Uses - {4}".format(invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.uses))

        else:
            del invites['Invites'][f"{invite.code}"]

            inv_name = invites['Invites'][invite.code]['name']
            if inv_name != "None":
                self.log(invite.guild.id, f"Invite {inv_name} - {invite.code} was deleted")
                await self.serverLog(invite.guild.id, "inv_deleted", "Invite {0} - https://discord.gg/{1} | Invite Channel - <#{2}>\nInviter - {3}\nMax Age - {4} | Uses - {5}".format(inv_name, invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.uses))
            else:
                self.log(invite.guild.id, f'Invite {invite.code} was deleted')
                await self.serverLog(invite.guild.id, "inv_deleted", "Invite - https://discord.gg/{0} | Invite Channel - <#{1}>\nInviter - {2}\nMax Age - {3} | Uses - {4}".format(invite.code, invite.channel.id, invite.inviter, invite.max_age, invite.uses))


        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot == True:
            return
        await self.add_inv_roles(await self.find_used_invite(member), member)

    async def add_inv_roles(self, invite, member):
        with open(f'configs/{member.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            if invites['Invites'][f"{invite}"]["roles"] == []:
                return
        except KeyError:
                # its the cool 1-inv escp, but we dont get member here due to sth, has to be fixed in the parent func
                # NoneType gets thrown here || await self.log(member.guild.id, f"There was this wild log here with a misdone configuration I have no mind for rn. Details:\nInvite Code: {invite}, Guild: {member.guild.id}, Member: {member}")
                #await self.log('0', f"There was this wild log here with a misdone configuration I have no mind for rn. Details:\nInvite Code: {invite}, Guild: '0', Member: {member}")
                return

        try:
            roles = []
            rolenames = []
            for role_id in invites['Invites'][f"{invite}"]["roles"]:
                role = member.guild.get_role(role_id)
                roles.append(role)
                rolenames.append(role.name)
            await member.add_roles(*roles)
            self.log(member.guild.id, f"Found invite roles: {rolenames} and roles were added")
        except KeyError:
            self.log(member.guild.id, f"No role for invite {invite}")

        try:
            with open(f'configs/{member.guild.id}.json', 'r') as f:
                invites = json.load(f)
            if invites["Invites"][f"{invite}"]["tags"]["1use"] == "used":

                inv_name = invites['Invites'][invite]['name']
                if inv_name != "None":
                    self.log(member.guild.id, f'Invite {inv_name} - {invite} marked as 1use was used')
                    await self.serverLog(member.guild.id, "inv_used", f"Invite {inv_name} - https://discord.gg/{invite}")
                else:
                    self.log(member.guild.id, f'Invite {invite} marked as 1use was used')
                    await self.serverLog(member.guild.id, "inv_used", f"Invite - https://discord.gg/{invite}")

                del invites['Invites'][f"{invite}"]

                with open(f'configs/{member.guild.id}.json', 'w') as f:
                    json.dump(invites, f, indent = 4)
        except KeyError:
            pass

        with open(f'configs/{member.guild.id}.json', 'r') as f:
            invites = json.load(f)

        # run the same code for retrieving used invites in find_used_invite to clearup unused 1use invites in this join
        invite_list = await member.guild.invites()
        srv_invites = {f"{invite.code}": {"uses": invite.uses} for invite in invite_list}
        if len(invites['Invites']) != len(srv_invites):
            for invite in list(invites['Invites'].keys()):
                if invite not in list(srv_invites.keys()):
                    del invites['Invites'][f"{invite}"]
                    break

        with open(f'configs/{member.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)


    async def find_used_invite(self, member):
        found_code = ''
        invite_list = await member.guild.invites()
        try:
            if await member.guild.vanity_invite() != None:
                invite_list.append(await member.guild.vanity_invite())
        except discord.HTTPException as msg_ex:
            if msg_ex.code == 50013 and msg_ex.status == 403:
                await ctx.send("Bot is missing permissions to see if vanity url is available")
                pass
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
                    if invites['Invites'][f"{invite.code}"]['name'] != "None":
                        self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code} named {invites['Invites'][invite.code]['name']}")
                        await self.serverLog(member.guild.id, "member_joined", "Member <@{0}>[`{1}`] joined with invite `{2}` named {3}".format(member.id, member.id, invite.code, invites['Invites'][invite.code]['name']))

                        if invites['Invites'][f"{invite.code}"]['welcome'] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = f"**InviteBot**", description = invites['Invites'][f"{invite.code}"]['welcome'], color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
                            now = datetime.datetime.now()
                            embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif invites['General']['WelcomeMessage'] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = f"**InviteBot**", description = invites['General']['WelcomeMessage'], color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
                            now = datetime.datetime.now()
                            embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)
                        found_code = invite.code
                        break

                    else:
                        self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code}")
                        await self.serverLog(member.guild.id, "member_joined", "Member <@{0}>[`{1}`] joined with invite `{2}`".format(member.id, member.id, invite.code))

                        if invites['Invites'][f"{invite.code}"]['welcome'] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = f"**InviteBot**", description = invites['Invites'][f"{invite.code}"]['welcome'], color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
                            now = datetime.datetime.now()
                            embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif invites['General']['WelcomeMessage'] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = f"**InviteBot**", description = invites['General']['WelcomeMessage'], color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
                            now = datetime.datetime.now()
                            embed.set_footer(text = f"{now.strftime('%H:%M')} / {now.strftime('%d/%m/%y')} | InviteBot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)
                        found_code = invite.code
                        break

            except KeyError:
                with open(f'configs/{member.guild.id}.json', 'r') as f:
                    invites = json.load(f)
                if uses[f"{invite.code}"] == 0:
                    try:
                        invites['Invites'][f"{invite.code}"]["uses"] = 0
                    except KeyError:
                        invites['Invites'][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None"}
                    self.log(invite.guild.id, f"New Invite {invite.code}")

                with open(f'configs/{member.guild.id}.json', 'w') as f:
                    json.dump(invites, f, indent = 4)

        for invite_code in uses:
            try:
                invites['Invites'][f"{invite_code}"]["uses"] = uses[f"{invite_code}"]
            except KeyError:
                try:
                    invites['Invites'][f"{invite_code}"] = {"name": "None", "roles": [], "uses": uses[f"{invite_code}"], "welcome": "None"}
                except KeyError:
                    invites['Invites'][f"{invite_code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None"}

        with open(f'configs/{invite.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

        if found_code == "":
            srv_invites = {f"{invite.code}": {"uses": invite.uses} for invite in invite_list}
            if len(invites['Invites']) != len(srv_invites):
                for invite in list(invites['Invites'].keys()):
                    if invite not in list(srv_invites.keys()):
                        found_code = invite
                        break

        return found_code

    @commands.command(aliases = ['inva'])
    async def add(self, ctx, invite: discord.Invite, role: discord.Role):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        bot_member = ctx.guild.get_member(self.client.user.id)
        if bot_member.top_role < role:
            await ctx.send("I cannot assign this role to users (Bot's role is below the role you want to assign)")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.append(role.id)
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] added role {role.name} to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_added", "{0}[`{1}`] linked role {2}[`{3}`] to {4}".format(ctx.author, ctx.author.id, role.name, role.id, invite.code))


        except KeyError:
            invites['Invites'][f"{invite.code}"] = {"name": "None", "roles": [role.id], "uses": 0, "welcome": "None"}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to add role {role.name} to non-existent in db invite, so it was created with starting role {role.name}")

        await ctx.send(f"Added role {role.name} to invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    @add.error
    async def add_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
            elif error.param.name == "role":
                await ctx.send("Your command is missing a required argument: a valid Discord role (Role meention or Role ID)")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invrem', 'invr'])
    async def remove(self, ctx, invite: discord.Invite, role: discord.Role = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        if role != "None":
            inv_roles = invites['Invites'][f"{invite.code}"]["roles"]
            inv_roles.remove(role.id)
            invites['Invites'][f"{invite.code}"]["roles"] = inv_roles

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed link from invite {invite.code} to role {role.name}")
            await self.serverLog(ctx.guild.id, "inv_removed", "{0}[`{1}`] removed the link of role {2}[`{3}`] to {4}".format(ctx.author, ctx.author.id, role.name, role.id, invite.code))

            await ctx.send(f"Removed link from invite {invite.code} to {role.name}")

        else:
            invites['Invites'][f"{invite.code}"]["roles"] = []

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed all links to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_removed", "{0}[`{1}`] removed all role links to {2}".format(ctx.author, ctx.author.id, invite.code))

            await ctx.send(f"Removed all links from invite {invite.code}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    @remove.error
    async def remove_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invn', 'rename'])
    async def name(self, ctx, invite: discord.Invite, name: str):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            old_name = invites['Invites'][f"{invite.code}"]["name"]
            invites['Invites'][f"{invite.code}"]["name"] = name
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] renamed invite {invite.code} from {old_name} to {name}")
            await self.serverLog(ctx.guild.id, "inv_rename", "{0}[`{1}`] renamed invite {2} from {3} to {4}".format(ctx.author, ctx.author.id, invite.code, old_name, name))


        except KeyError:
            invites['Invites'][f"{invite.code}"] = {"name": f"{name}", "roles": [], "uses": 0, "welcome": "None"}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to rename a non-existent in db invite, so it was created")

        await ctx.send(f"Renamed {invite.code} from {old_name} to {name}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    @name.error
    async def name_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
            elif error.param.name == "name":
                await ctx.send("Your command is missing a required argument: a name for your invite")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invw'])
    async def welcome(self, ctx, invite: discord.Invite, welcome: str):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            old_welcome = invites['Invites'][f"{invite.code}"]["welcome"]
            invites['Invites'][f"{invite.code}"]["welcome"] = welcome
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] changed the welcome message of invite {invite.code} from {old_welcome} to {welcome}")
            await self.serverLog(ctx.guild.id, "inv_welcome", "{0}[`{1}`] changed the welcome message of invite {2} from {3} to {4}".format(ctx.author, ctx.author.id, invite.code, old_welcome, welcome))


        except KeyError:
            invites['Invites'][f"{invite.code}"] = {"name": f"None", "roles": [], "uses": 0, "welcome": f"{welcome}"}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to change the welcome message of a non-existent in db invite, so it was created")

        await ctx.send(f"Changed the welcome message of invite {invite.code} from {old_welcome} to {welcome}")

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    @welcome.error
    async def welcome_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
            elif error.param.name == "name":
                await ctx.send("Your command is missing a required argument: a welcome message to be tied with your invite")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invlist', 'invls'])
    async def list(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        if len(invites['Invites']) == 0:
            await ctx.send("You have no invites")
            return

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
                if invites['Invites'][f'{inv}']['name'] != "None":
                    embed.add_field(name = f"{invites['Invites'][inv]['name']}", value = f"https://discord.gg/{inv}\n{about}", inline = True)
                else:
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
    async def make(self, ctx, channel: discord.TextChannel, name: str = "None", role: discord.Role = 0, uses: int = 0, age: int = 0):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        bot_member = ctx.guild.get_member(self.client.user.id)
        if role != 0:
            if bot_member.top_role < role:
                await ctx.send("I cannot assign this role to users (Bot's role is below the role you want to assign)")
                return

        with open(f'configs/{ctx.guild.id}.json', 'r') as f:
            invites = json.load(f)

        try:
            invite = await channel.create_invite(max_age = age, max_uses = uses)
        except discord.HTTPException as msg_ex:
            if msg_ex.code == 50013 and msg_ex.status == 403:
                await ctx.send("Bot is missing permissions to create an invite.\n[https://docs.invitebot.xyz/error-helpers/#bot-is-missing-permissions-to-create-an-invite]")
                return

        invites['Invites'][f"{invite.code}"] = {}
        invites['Invites'][f"{invite.code}"]['name'] = name
        if role != 0:
            invites['Invites'][f"{invite.code}"]['roles'] = [role.id]
        else:
            invites['Invites'][f"{invite.code}"]['roles'] = []
        invites['Invites'][f"{invite.code}"]['uses'] = uses
        invites['Invites'][f"{invite.code}"]['welcome'] = "None"
        invites['Invites'][f"{invite.code}"]['tags'] = {}
        if uses == 1:
            invites['Invites'][f"{invite.code}"]['tags']['1use'] = True

        if name == "None":
            if role == 0:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} in {channel}, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel}n, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", "<@{0}>[`{1}`] created invite `https://discord.gg/{2}` in {3} with {4} on join, age: {5} and uses: {6}".format(ctx.author.id, ctx.author.id, invite.code, channel, role, invite.max_age, invite.max_uses))
            else:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} in {channel} with {role} on join, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel} with {role} on join, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", "<@{0}>[`{1}`] created invite `https://discord.gg/{2}` in {3}, age: {4} and uses: {5}".format(ctx.author.id, ctx.author.id, invite.code, channel, invite.max_age, invite.max_uses))
        else:
            if role == 0:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} named {name} in {channel}, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel}, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", "<@{0}>[`{1}`] created invite `https://discord.gg/{2} named {3}` in {4}, age: {5} and uses: {6}".format(ctx.author.id, ctx.author.id, invite.code, name, channel, invite.max_age, invite.max_uses))
            else:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} named {name} in {channel} with {role} on join, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel} with {role} on join, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", "<@{0}>[`{1}`] created invite `https://discord.gg/{2} named {3}` in {4} with {5} on join, age: {6} and uses: {7}".format(ctx.author.id, ctx.author.id, invite.code, name, channel, role, invite.max_age, invite.max_uses))

        with open(f'configs/{ctx.guild.id}.json', 'w') as f:
            json.dump(invites, f, indent = 4)

    @make.error
    async def make_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "channel":
                await ctx.send("Your command is missing a required argument: a valid channel (Channel mention or Channel ID)")
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invdel', 'invd'])
    async def delete(self, ctx, invite: discord.Invite):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay=3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        try:
            await invite.delete()
            self.log(ctx.guild.id, f"{ctx.author}[{ctx.author.id}] deleted invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_deleted", f"{ctx.author}[`{ctx.author.id}`] deleted invite {invite.code}")
        except discord.HTTPException as msg_ex:
            if msg_ex.code == 50013 and msg_ex.status == 403:
                await ctx.send("Bot is missing permissions to delete an invite.")
                return

    @delete.error
    async def delete_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

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

    def checkPerms(self, user_id, guild_id, addscopes = []):
        with open(f'configs/{guild_id}.json', 'r') as f:
            config = json.load(f)
            admin_roles = config['General']['AdminRoles']
        with open(f'main-config.json', 'r') as f:
            main_config = json.load(f)
            owners = main_config['OwnerUsers']

        isAble = 0

        guild = self.client.get_guild(guild_id)
        member = guild.get_member(user_id)

        if "owner_only" in addscopes:
            if user_id == guild.owner_id:
                return True

        if "owner_users_only" in addscopes:
            if user_id in owners:
                return True

        if user_id in owners:
            isAble += 1
        if user_id == guild.owner_id:
            isAble += 1
        for role in member.roles:
            if role.id in admin_roles:
                isAble += 1

        if "admin" in addscopes:
            if member.guild_permissions.administrator == True:
                isAble += 1
        if "manage_guild" in addscopes:
            if member.guild_permissions.manage_guild == True:
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
        embed.set_thumbnail(url="https://invitebot.xyz/icons/invitebot-logo.png")
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
        if type in ["member_joined", "inv_rename", "inv_welcome"]:
            em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["inv_deleted", "inv_removed", "inv_used"]:
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
        if type == "inv_rename":
            embed.add_field(name = "Invite Renamed", value = log_msg, inline = False)
        if type == "inv_welcome":
            embed.add_field(name = "Invite Changed Welcome Message", value = log_msg, inline = False)
        if type == "inv_deleted":
            embed.add_field(name = "Invite Deleted", value = log_msg, inline = False)
        if type == "inv_used":
            embed.add_field(name = "Invite marked as 1use Used", value = log_msg, inline = False)
        if type == "inv_removed":
            embed.add_field(name = "Invite-Role Link Removed", value = log_msg, inline = False)

        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(embed = embed)

def setup(client):
    client.add_cog(Invs(client))
