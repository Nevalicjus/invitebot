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
        with open(f"configs/{invite.guild.id}.json", "r") as f:
            config = json.load(f)

        config["Invites"][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {}}
        if ("COMMUNITY" in invite.guild.features) and ("MEMBER_VERIFICATION_GATE_ENABLED" in invite.guild.features):
            if config["General"]["AwaitRulesAccept"] == True:
                config["Invites"][f"{invite.code}"]["tags"]["awaitrules"] = True
        if invite.max_uses == 1:
            config["Invites"][f"{invite.code}"]["tags"]["1use"] = True


        with open(f"configs/{invite.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

        self.log(invite.guild.id, f"Invite {invite.code} was created")
        await self.serverLog(invite.guild.id, "inv_created", f"Invite - https://discord.gg/{invite.code}\nInvite Channel - <#{invite.channel.id}>\nInviter - {invite.inviter}\nMax Age - {invite.max_age}\nMax Uses - {invite.max_uses}")

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        with open(f"configs/{invite.guild.id}.json", "r") as f:
            config = json.load(f)

        # run the same code for retrieving used invites in find_used_invite to clearup unused 1use invites in this join
        #print("Running 1use clearer")
        invite_list = await invite.guild.invites()
        srv_invites = {f"{inv.code}": {"uses": inv.uses} for inv in invite_list}
        if len(config["Invites"]) != len(srv_invites):
            for inv in config["Invites"]:
                try:
                    if ((inv not in srv_invites) and (config["Invites"][inv]["tags"]["1use"] == "used")):
                        del config["Invites"][f"{inv}"]
                        break
                except KeyError:
                    pass

        # if invite is a 1use, marked it as used so addinvroles can read roles and then delete the inv
        if "1use" in config["Invites"][f"{invite.code}"]["tags"]:
            if config["Invites"][f"{invite.code}"]["tags"]["1use"] == True:
                config["Invites"][f"{invite.code}"]["tags"]["1use"] = "used"

                inv_name = config["Invites"][f"{invite.code}"]['name']
                if inv_name != "None":
                    self.log(invite.guild.id, f"Invite {inv_name} - {invite.code} marked as 1use was deleted")
                    await self.serverLog(invite.guild.id, "inv_deleted", f"Invite {inv_name} - https://discord.gg/{invite.code}\nInvite Channel - <#{invite.channel.id}>\nInviter - {invite.inviter}\nMax Age - {invite.max_age}\nUses - {invite.uses}")
                else:
                    self.log(invite.guild.id, f"Invite {invite.code} marked as 1use was deleted")
                    await self.serverLog(invite.guild.id, "inv_deleted", f"Invite - https://discord.gg/{invite.code}\nInvite Channel - <#{invite.channel.id}>\nInviter - {invite.inviter}\nMax Age - {invite.max_age}\nUses - {invite.uses}")

        else:
            inv_name = config["Invites"][f"{invite.code}"]["name"]
            if inv_name != "None":
                self.log(invite.guild.id, f"Invite {inv_name} - {invite.code} was deleted")
                await self.serverLog(invite.guild.id, "inv_deleted", f"Invite {inv_name} - https://discord.gg/{invite.code}\nInvite Channel - <#{invite.channel.id}>\nInviter - {invite.inviter}\nMax Age - {invite.max_age}\nUses - {invite.uses}")
            else:
                self.log(invite.guild.id, f"Invite {invite.code} was deleted")
                await self.serverLog(invite.guild.id, "inv_deleted", f"Invite - https://discord.gg/{invite.code}\nInvite Channel - <#{invite.channel.id}>\nInviter - {invite.inviter}\nMax Age - {invite.max_age}\nUses - {invite.uses}")
            del config["Invites"][f"{invite.code}"]

        with open(f"configs/{invite.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot == True:
            return
        await asyncio.sleep(1)
        await self.add_inv_roles(await self.find_used_invite(member), member)

    async def add_inv_roles(self, invite, member):
        with open(f"configs/{member.guild.id}.json", "r") as f:
            config = json.load(f)

        try:
            if config["Invites"][f"{invite}"]["roles"] != []:
                roles = []
                rolenames = []
                for role_id in config["Invites"][f"{invite}"]["roles"]:
                    role = member.guild.get_role(role_id)
                    roles.append(role)
                    rolenames.append(role.name)

                # community server & rule screening checkpart
                if ("COMMUNITY" in member.guild.features) and ("MEMBER_VERIFICATION_GATE_ENABLED" in member.guild.features):
                    if (config["General"]["AwaitRulesAccept"] == True) and (config["Invites"][f"{invite}"]["tags"]["awaitrules"] == True):
                        while member.pending == True:
                            # awaiting user rules acceptance
                            await asyncio.sleep(3)

                await member.add_roles(*roles)
                self.log(member.guild.id, f"Found invite roles: {rolenames} and roles were added")
            else:
                self.log(member.guild.id, f"No role for invite {invite}")
        except KeyError:
            self.log(member.guild.id, f"No role for invite {invite}")

        try:
            if config["Invites"][f"{invite}"]["tags"]["1use"] == "used":
                inv_name = config["Invites"][f"{invite}"]["name"]
                if inv_name != "None":
                    self.log(member.guild.id, f"Invite {inv_name} - {invite} marked as 1use was used")
                    await self.serverLog(member.guild.id, "inv_used", f"Invite {inv_name} - https://discord.gg/{invite}")
                else:
                    self.log(member.guild.id, f"Invite {invite} marked as 1use was used")
                    await self.serverLog(member.guild.id, "inv_used", f"Invite - https://discord.gg/{invite}")

                del config["Invites"][f"{invite}"]
        except KeyError:
            pass

        srv_invites = {}
        for inv in await member.guild.invites():
            try:
                srv_invites[f"{inv.code}"] = {"inviter": inv.inviter.id}
            except:
                # landing here probably means there is a desync between invites fetched at the start of iterating and through it
                # i have no idea what could cause that
                pass
        #srv_invites = {f"{inv.code}": {"inviter": inv.inviter.id} for inv in await member.guild.invites()}
        if f"{invite}" in srv_invites:
            await self.analytics_add(member.guild.id, member.id, srv_invites[f"{invite}"]["inviter"], 1)
        else:
            # landing here means 1use invite was used
            # this is #1 not useful to track as I cant imagine anyone wanting to create an invite with 1 use for inviting as many poor souls as he can
            # and #2 this would meam we have to mark the inviter in the invites dict in config as 1use invites won't fetch us inviter.ids as the invite doesnt exist on remote
            # it can certainly be done, but at this very moment I do not see the need to
            pass

        # run the same code for retrieving used invites in find_used_invite to clearup unused 1use invites in this join
        #print("Running 1use clearer")
        srv_invites = {f"{invite.code}": {"uses": invite.uses} for invite in await member.guild.invites()}
        if len(config["Invites"]) != len(srv_invites):
            for invite in config["Invites"]:
                if invite not in srv_invites:
                    del config["Invites"][f"{invite}"]
                    break

        with open(f"configs/{member.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

    async def find_used_invite(self, member):
        found_code = ""
        invite_list = await member.guild.invites()
        try:
            if await member.guild.vanity_invite() != None:
                invite_list.append(await member.guild.vanity_invite())
        except discord.HTTPException as msg_ex:
            if msg_ex.code == 50013 and msg_ex.status == 403:
                #await ctx.send("Bot is missing permissions to see if vanity url is available")
                self.log("0", "Bot is missing permissions to see if vanity url is available")
                pass
        uses = {}

        with open(f"configs/{member.guild.id}.json", "r") as f:
            config = json.load(f)
        curr_uses = {}

        for invite in config["Invites"]:
            curr_uses[f"{invite}"] = config["Invites"][f"{invite}"]["uses"]

        for invite in invite_list:
            uses[f"{invite.code}"] = invite.uses
            try:
                if (uses[f"{invite.code}"] != curr_uses[f"{invite.code}"]) and (uses[f"{invite.code}"] != 0):
                    if config["Invites"][f"{invite.code}"]["name"] != "None":
                        self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code} named {config['Invites'][invite.code]['name']}")
                        await self.serverLog(member.guild.id, "member_joined", f"Member <@{member.id}>[`{member.id}`] joined with invite `{invite.code}` named {config['Invites'][invite.code]['name']}")

                        if config["Invites"][f"{invite.code}"]["welcome"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["Invites"][f"{invite.code}"]["welcome"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif config["General"]["WelcomeMessage"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["General"]["WelcomeMessage"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)
                        found_code = invite.code
                        break

                    else:
                        self.log(invite.guild.id, f"User {member.name}[{member.id}] joined with invite {invite.code}")
                        await self.serverLog(member.guild.id, "member_joined", f"Member <@{member.id}>[`{member.id}`] joined with invite `{invite.code}`")

                        if config["Invites"][f"{invite.code}"]["welcome"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["Invites"][f"{invite.code}"]["welcome"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif config["General"]["WelcomeMessage"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["General"]["WelcomeMessage"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)
                        found_code = invite.code
                        break

            except KeyError:
                if uses[f"{invite.code}"] == 0:
                    try:
                        config["Invites"][f"{invite.code}"]["uses"] = 0
                    except KeyError:
                        config["Invites"][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {}}
                    self.log(invite.guild.id, f"New Invite {invite.code}")

        for invite_code in uses:
            try:
                config["Invites"][f"{invite_code}"]["uses"] = uses[f"{invite_code}"]
            except KeyError:
                try:
                    config["Invites"][f"{invite_code}"] = {"name": "None", "roles": [], "uses": uses[f"{invite_code}"], "welcome": "None", "tags": {}}
                except KeyError:
                    config["Invites"][f"{invite_code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {}}

        with open(f"configs/{member.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

        srv_invites = {f"{invite.code}": {"uses": invite.uses} for invite in invite_list}
        if (len(config["Invites"]) != len(srv_invites)) and (found_code == ""):
            for invite in config['Invites']:
                if invite not in srv_invites:
                    if config["Invites"][f"{invite}"]["name"] != "None":
                        self.log(member.guild.id, f"User {member.name}[{member.id}] joined with invite {invite} named {config['Invites'][invite]['name']}")
                        await self.serverLog(member.guild.id, "member_joined", f"Member <@{member.id}>[`{member.id}`] joined with invite `{invite}` named {config['Invites'][invite]['name']}")

                        if config["Invites"][f"{invite}"]["welcome"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["Invites"][f"{invite}"]["welcome"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif config["General"]["WelcomeMessage"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["General"]["WelcomeMessage"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                    else:
                        self.log(member.guild.id, f"User {member.name}[{member.id}] joined with invite {invite}")
                        await self.serverLog(member.guild.id, "member_joined", f"Member <@{member.id}>[`{member.id}`] joined with invite `{invite}`")

                        if config["Invites"][f"{invite}"]["welcome"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["Invites"][f"{invite}"]["welcome"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)

                        elif config["General"]["WelcomeMessage"] != "None":
                            recipient = self.client.get_user(member.id)
                            embed = discord.Embed(title = "**Invitebot**", description = config["General"]["WelcomeMessage"], timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
                            embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
                            embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
                            await recipient.send(embed = embed)
                    found_code = invite
                    break

        return found_code

    @commands.command(aliases = ["inva"])
    async def add(self, ctx, invite: discord.Invite, role: discord.Role):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        bot_member = ctx.guild.get_member(self.client.user.id)
        if bot_member.top_role < role:
            await ctx.send("I cannot assign this role to users (Bot's role is below the role you want to assign)")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        try:
            inv_roles = config["Invites"][f"{invite.code}"]["roles"]
            inv_roles.append(role.id)
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] added role {role.name} to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_added", f"<@{ctx.author.id}>[`{ctx.author.id}`] linked role {role.name}[`{role.id}`] to {invite.code}")


        except KeyError:
            config["Invites"][f"{invite.code}"] = {"name": "None", "roles": [role.id], "uses": 0, "welcome": "None", "tags": {}}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to add role {role.name} to non-existent in db invite, so it was created with starting role {role.name}")

        await ctx.send(f"Added role {role.name} to invite {invite.code}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

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

    @commands.command(aliases = ["invrem", "invr"])
    async def remove(self, ctx, invite: discord.Invite, role: discord.Role = "None"):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        if role != "None":
            inv_roles = config["Invites"][f"{invite.code}"]["roles"]
            inv_roles.remove(role.id)
            config["Invites"][f"{invite.code}"]["roles"] = inv_roles

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed link from invite {invite.code} to role {role.name}")
            await self.serverLog(ctx.guild.id, "inv_removed", f"<@{ctx.author.id}>[`{ctx.author.id}`] removed the link of role {role.name}[`{role.id}`] to {invite.code}")
            await ctx.send(f"Removed link from invite {invite.code} to {role.name}")

        else:
            config["Invites"][f"{invite.code}"]["roles"] = []

            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] removed all links to invite {invite.code}")
            await self.serverLog(ctx.guild.id, "inv_removed", f"<@{ctx.author.id}>[`{ctx.author.id}`] removed all role links to {invite.code}")
            await ctx.send(f"Removed all links from invite {invite.code}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

    @remove.error
    async def remove_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ["invn", "rename"])
    async def name(self, ctx, invite: discord.Invite, name: str):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        try:
            old_name = config["Invites"][f"{invite.code}"]["name"]
            config["Invites"][f"{invite.code}"]["name"] = name
            self.log(invite.guild.id, f"<@{ctx.author.id}>[{ctx.author.id}] renamed invite {invite.code} from {old_name} to {name}")
            await self.serverLog(ctx.guild.id, "inv_rename", f"<@{ctx.author.id}>[`{ctx.author.id}`] renamed invite {invite.code} from {old_name} to {name}")

        except KeyError:
            config["Invites"][f"{invite.code}"] = {"name": f"{name}", "roles": [], "uses": 0, "welcome": "None", "tags": {}}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to rename a non-existent in db invite, so it was created")

        await ctx.send(f"Renamed {invite.code} from {old_name} to {name}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

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

    @commands.command(aliases = ["invw"])
    async def welcome(self, ctx, invite: discord.Invite, welcome: str):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        try:
            old_welcome = config["Invites"][f"{invite.code}"]["welcome"]
            config["Invites"][f"{invite.code}"]["welcome"] = welcome
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] changed the welcome message of invite {invite.code} from {old_welcome} to {welcome}")
            await self.serverLog(ctx.guild.id, "inv_welcome", f"{ctx.author}[`{ctx.author.id}`] changed the welcome message of invite {invite.code} from {old_welcome} to {welcome}")

        except KeyError:
            config["Invites"][f"{invite.code}"] = {"name": f"None", "roles": [], "uses": 0, "welcome": f"{welcome}", "tags": {}}
            self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to change the welcome message of a non-existent in db invite, so it was created")

        await ctx.send(f"Changed the welcome message of invite {invite.code} from {old_welcome} to {welcome}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

    @welcome.error
    async def welcome_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
            elif error.param.name == "welcome":
                await ctx.send("Your command is missing a required argument: a welcome message to be tied with your invite")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ["invar"])
    async def awaitrules(self, ctx, invite: discord.Invite, choice):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        if choice in ["true", "yes", "y", "allow", "enable", "1"]:
            choice = True
        if choice in ["false", "no", "n", "deny", "disable", "0"]:
            choice = False
        if choice not in [True, False]:
            embed = self.constructResponseEmbedBase("This is not a valid input")
            await ctx.send(embed = embed)
            return

        try:
            config["Invites"][f"{invite.code}"]["tags"]["awaitrules"] = choice
            if choice == True:
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] enabled awaiting rules of invite {invite.code}")
                await self.serverLog(ctx.guild.id, "inv_awaitrules", f"{ctx.author}[`{ctx.author.id}`] enabled awaiting rules of invite {invite.code}")

            if choice == False:
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] disable awaiting rules of invite {invite.code}")
                await self.serverLog(ctx.guild.id, "inv_awaitrules", f"{ctx.author}[`{ctx.author.id}`] disabled awaiting rules of invite {invite.code}")

        except KeyError:
            if choice == True:
                config["Invites"][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {"awaitrules": True}}
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to enable awaiting rules of a non-existent in db invite, so it was created")
            if choice == False:
                config["Invites"][f"{invite.code}"] = {"name": "None", "roles": [], "uses": 0, "welcome": "None", "tags": {"awaitrules": False}}
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] tried to disable awaiting rules of a non-existent in db invite, so it was created")

        if choice == True:
            await ctx.send(f"Enabled awaiting rules of invite {invite.code}")
        if choice == False:
            await ctx.send(f"Disabled awaiting rules of invite {invite.code}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

    @awaitrules.error
    async def awaitrules_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "invite":
                await ctx.send("Your command is missing a required argument: a valid Discord invite link or invite code")
            elif error.param.name == "choice":
                await ctx.send("Please provide an option for the setting (yes/no)")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")

        #await self.errorLog()

    @commands.command(aliases = ['invlist', 'invls'])
    async def list(self, ctx):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin", "manage_guild"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        l = []
        for inv in config["Invites"]:
            if "1use" in config["Invites"][f"{inv}"]["tags"]:
                if config["Invites"][f"{inv}"]["tags"]["1use"] != "used":
                    l.append(inv)
            else:
                l.append(inv)
        if len(l) == 0:
            await ctx.send("You have no invites")
            return

        no_fields = 0

        embed = discord.Embed(title = "**Invite List**", timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url = ctx.guild.icon_url_as(format = "png"))
        embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")

        for inv in config["Invites"]:
            if "1use" in config["Invites"][f"{inv}"]["tags"]:
                if config["Invites"][f"{inv}"]["tags"]["1use"] == "used":
                    continue
            about = ""
            for invrole in config["Invites"][f"{inv}"]["roles"]:
                role = ctx.guild.get_role(invrole)
                about += f"{role.name}\n"
            about += f"Uses - {config['Invites'][inv]['uses']}\n"
            if about != "":
                if config["Invites"][f"{inv}"]["name"] != "None":
                    embed.add_field(name = f"{config['Invites'][inv]['name']}", value = f"https://discord.gg/{inv}\n{about}", inline = True)
                else:
                    embed.add_field(name = f"https://discord.gg/{inv}", value = about, inline = True)
                no_fields += 1
            if no_fields == 25:
                await ctx.send(embed = embed)
                no_fields = 0
                for i in range(25):
                    embed.remove_field(0)
        if no_fields != 0:
            await ctx.send(embed = embed)

    @commands.command(aliases = ["invm"])
    async def make(self, ctx, channel: discord.TextChannel, name: str = "None", role: discord.Role = 0, uses: int = 0, age: int = 0):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        bot_member = ctx.guild.get_member(self.client.user.id)
        if role != 0:
            if bot_member.top_role < role:
                await ctx.send("I cannot assign this role to users (Bot's role is below the role you want to assign)")
                return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        try:
            invite = await channel.create_invite(max_age = age, max_uses = uses)
        except discord.HTTPException as msg_ex:
            if msg_ex.code == 50013 and msg_ex.status == 403:
                await ctx.send("Bot is missing permissions to create an invite.\n[https://docs.invitebot.xyz/error-helpers/#bot-is-missing-permissions-to-create-an-invite]")
                return

        config["Invites"][f"{invite.code}"] = {}
        config["Invites"][f"{invite.code}"]["name"] = name
        if role != 0:
            config["Invites"][f"{invite.code}"]["roles"] = [role.id]
        else:
            config["Invites"][f"{invite.code}"]['roles'] = []
        config["Invites"][f"{invite.code}"]["uses"] = uses
        config["Invites"][f"{invite.code}"]["welcome"] = "None"
        config["Invites"][f"{invite.code}"]["tags"] = {}
        if uses == 1:
            config['Invites'][f"{invite.code}"]["tags"]["1use"] = True
        if ("COMMUNITY" in invite.guild.features) and ("MEMBER_VERIFICATION_GATE_ENABLED" in invite.guild.features):
            if config["General"]["AwaitRulesAccept"] == True:
                config["Invites"][f"{invite.code}"]["tags"]["awaitrules"] = True

        if name == "None":
            if role == 0:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} in {channel}, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel}, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` in {channel}, age: {invite.max_age} and uses: {invite.max_uses}")
            else:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} in {channel} with {role} on join, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel} with {role} on join, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` in {channel} with {role} on join, age: {invite.max_age} and uses: {invite.max_uses}")
        else:
            if role == 0:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} named {name} in {channel}, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel}, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code} named {name}` in {channel}, age: {invite.max_age} and uses: {invite.max_uses}")
            else:
                await ctx.send(f"{ctx.author}[`{ctx.author.id}`] created an invite https://discord.gg/{invite.code} named {name} in {channel} with {role} on join, age: {age} and uses: {uses}")
                self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel} with {role} on join, age: {age} and uses: {uses}")
                await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code} named {name}` in {channel} with {role} on join, age: {invite.max_age} and uses: {invite.max_uses}")

        with open(f"configs/{ctx.guild.id}.json", "w") as f:
            json.dump(config, f, indent = 4)

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

    @commands.command(aliases = ["invmm"])
    @commands.cooldown(1.0, 30.0, commands.BucketType.guild)
    async def massmake(self, ctx, num: int, channel: discord.TextChannel, name: str = "None", role: discord.Role = 0, uses: int = 0, age: int = 0):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

        if self.checkPerms(ctx.author.id, ctx.guild.id, ["admin"]) == False:
            await ctx.send("You are not permitted to run this command")
            return

        bot_member = ctx.guild.get_member(self.client.user.id)
        if role != 0:
            if bot_member.top_role < role:
                await ctx.send("I cannot assign this role to users (Bot's role is below the role you want to assign)")
                return

        if num > 20:
            await ctx.send("For rate limiting reasons, you can create a maximum of 20 invites at a time")
            return

        with open(f"configs/{ctx.guild.id}.json", "r") as f:
            config = json.load(f)

        genned_invs = []

        for i in range(0, int(num)):
            await asyncio.sleep(1)
            inv_name = f"{name}-{i}"

            try:
                invite = await channel.create_invite(max_age = age, max_uses = uses)
            except discord.HTTPException as msg_ex:
                if msg_ex.code == 50013 and msg_ex.status == 403:
                    await ctx.send("Bot is missing permissions to create an invite.\n[https://docs.invitebot.xyz/error-helpers/#bot-is-missing-permissions-to-create-an-invite]")
                    return

            with open(f"configs/{ctx.guild.id}.json", "r") as f:
                invites = json.load(f)

            config["Invites"][f"{invite.code}"] = {}
            config["Invites"][f"{invite.code}"]["name"] = inv_name
            if role != 0:
                config["Invites"][f"{invite.code}"]["roles"] = [role.id]
            else:
                config["Invites"][f"{invite.code}"]["roles"] = []
            config["Invites"][f"{invite.code}"]["uses"] = uses
            config["Invites"][f"{invite.code}"]["welcome"] = "None"
            config["Invites"][f"{invite.code}"]["tags"] = {}
            if uses == 1:
                config["Invites"][f"{invite.code}"]["tags"]["1use"] = True
            if ("COMMUNITY" in invite.guild.features) and ("MEMBER_VERIFICATION_GATE_ENABLED" in invite.guild.features):
                if config["General"]["AwaitRulesAccept"] == True:
                    config["Invites"][f"{invite.code}"]["tags"]["awaitrules"] = True

            if name == "None":
                if role == 0:
                    self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel}n, age: {age} and uses: {uses}")
                    await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` in {channel} with {role} on join, age: {invite.max_age} and uses: {invite.max_uses}")
                else:
                    self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} in {channel} with {role} on join, age: {age} and uses: {uses}")
                    await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` in {channel}, age: {invite.max_age} and uses: {invite.max_uses}")
            else:
                if role == 0:
                    self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel}, age: {age} and uses: {uses}")
                    await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` named {name} in {channel}, age: {invite.max_age} and uses: {invite.max_uses}")
                else:
                    self.log(invite.guild.id, f"{ctx.author}[{ctx.author.id}] created an invite https://discord.gg/{invite.code} named {name} in {channel} with {role} on join, age: {age} and uses: {uses}")
                    await self.serverLog(ctx.guild.id, "inv_made", f"<@{ctx.author.id}>[`{ctx.author.id}`] created invite `https://discord.gg/{invite.code}` named {name} in {channel} with {role} on join, age: {invite.max_age} and uses: {invite.max_uses}")

            genned_invs.append(f"Invite `{inv_name}` - <https://discord.gg/{invite.code}>\n")
            with open(f"configs/{ctx.guild.id}.json", "w") as f:
                json.dump(config, f, indent = 4)

        await ctx.send(f"Generated {num} invites:\n{''.join(line for line in genned_invs)}")

    @massmake.error
    async def massmake_err_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == "num":
                await ctx.send("Your command is missing a required argument: a valid integer")
            if error.param.name == "channel":
                await ctx.send("Your command is missing a required argument: a valid channel (Channel mention or Channel ID)")
        if isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.RoleNotFound):
            await ctx.send("Role you are trying to mention or provide ID of doesn't exist")
        if isinstance(error, commands.BadInviteArgument):
            await ctx.send("Invite you are trying to use is invalid or expired")
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You are trying to use this command too fast. Cooldown is 30s and you can run your command in {self.massmake.get_cooldown_retry_after(ctx)}")

        #await self.errorLog()

    @commands.command(aliases = ["invdel", "invd"])
    async def delete(self, ctx, invite: discord.Invite):
        if self.checkInvos(ctx.guild.id) == 1:
            await ctx.message.delete(delay = 3)

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

    async def analytics_add(self, guild_id, user_id, inviter_id, num):
        if f"{guild_id}.json" not in os.listdir("users/"):
            users_blank = {}
            with open(f"users/{guild_id}.json", "w") as f:
                json.dump(users_blank, f, indent = 4)
        with open(f"users/{guild_id}.json", "r") as f:
            users = json.load(f)

        if f"{inviter_id}" not in users:
            users[f"{inviter_id}"] = {}
            users[f"{inviter_id}"]["NumberOfInvited"] = 0
        else:
            users[f"{inviter_id}"]["NumberOfInvited"] += num

        with open(f"users/{guild_id}.json", "w") as f:
            json.dump(users, f, indent = 4)

        with open(f"configs/{guild_id}.json", "r") as f:
            config = json.load(f)

        if (config["General"]["Analytics"] == True) and (config["General"]["AnalyticsLog"] != 0):
            guild = self.client.get_guild(guild_id)
            analytics_channel = self.client.get_channel(config["General"]["AnalyticsLog"])
            joiner = guild.get_member(user_id)
            inviter = guild.get_member(inviter_id)

            if users[f"{inviter_id}"]["NumberOfInvited"] == 1:
                flex = "person"
            else:
                flex = "people"
            embed = self.constructResponseEmbedBase(f"User {joiner.mention} was invited by {inviter.mention}\n{inviter.mention} has altogether invited {users[f'{inviter_id}']['NumberOfInvited']} {flex} 🎉")
            await analytics_channel.send(embed = embed)

    def log(self, guild_id, log_msg: str):
        with open("main-config.json", "r") as f:
            config = json.load(f)
        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[33mINVROLES\033[0m]: {log_msg}")
            with open(f"{config['LogFile']}", "a") as f:
                f.write(f"[{datetime.datetime.now()}] [INVROLES]: {log_msg}\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[33mINVROLES\033[0m]: {log_msg}")
            with open(f"{config['LogFile']}", "a") as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [INVROLES]: {log_msg}\n")

    def checkPerms(self, user_id, guild_id, addscopes = []):
        with open(f"configs/{guild_id}.json", "r") as f:
            config = json.load(f)
            admin_roles = config["General"]["AdminRoles"]
        with open(f"main-config.json", "r") as f:
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
        with open(f"configs/{guild_id}.json", "r") as f:
            config = json.load(f)
            delinvos = config["General"]["DeleteInvocations"]

        if delinvos == 1:
            return True
        else:
            return False

    def constructResponseEmbedBase(self, desc):
        embed = discord.Embed(title = "**Invitebot**", description = desc, timestamp = datetime.datetime.utcnow(), color = discord.Colour.from_rgb(119, 137, 218))
        embed.set_thumbnail(url = "https://invitebot.xyz/icons/invitebot-logo.png")
        embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")
        return embed

    async def serverLog(self, guild_id, type, log_msg):
        with open(f"configs/{guild_id}.json", "r") as f:
            config = json.load(f)
            log_channel_id = config["General"]["ServerLog"]
        if log_channel_id == 0:
            return False

        if type in ["inv_created", "inv_added", "inv_made"]:
            em_color = discord.Colour.from_rgb(67, 181, 129)
        if type in ["member_joined", "inv_rename", "inv_welcome", "inv_awaitrules"]:
            em_color = discord.Colour.from_rgb(250, 166, 26)
        if type in ["inv_deleted", "inv_removed", "inv_used"]:
            em_color = discord.Colour.from_rgb(240, 71, 71)

        embed = discord.Embed(title = "**Invitebot Logging**", color = em_color)
        embed.set_footer(text = "Support Server - https://invitebot.xyz/support \nInvitebot made with \u2764\ufe0f by Nevalicjus")

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
        if type == "inv_awaitrules":
            embed.add_field(name = "Invite Changed Await Rules status", value = log_msg, inline = False)
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
