import discord
import traceback
import sys
import os
import json
import datetime
from discord.ext import commands

class CommandErrorHandler(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            owners = config['OwnerUsers']

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        #ignored = (commands.CommandNotFound, )
        ignored = (0)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        temp_trace = ""
        for line in traceback.format_exception(type(error), error, error.__traceback__):
            temp_trace += line
        trace = temp_trace[:-1]
        for owner in owners:
            recipient = self.client.get_user(owner)
            try:
                await recipient.send(f"There was an error that happened in {ctx.guild.name}[{ctx.guild.id}] caused by {ctx.message.content}, which was run by {ctx.author.name}[{ctx.author.id}]:\n```{trace}```")
            except discord.HTTPException as msg_ex:
                if msg_ex.code == 50035 and msg_ex.status == 400:
                    now = datetime.datetime.now()
                    temp_file_name = now.strftime('temp-err-trace-%H%M%S-%d%m%y.txt')
                    f = open(f"{temp_file_name}", "w")
                    f.write(f"There was an error that happened in {ctx.guild.name}[{ctx.guild.id}] caused by {ctx.message.content}, which was run by {ctx.author.name}[{ctx.author.id}]:\n {trace}")
                    f.close()
                    await recipient.send(f"There was an error:", file=discord.File(f'{temp_file_name}'))
                    os.remove(f"{temp_file_name}")


        # return if we ignore an exception
        #if isinstance(error, ignored):
        #    return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        else:
            # other errs
            self.log(ctx.guild.id, f'Ignoring exception that happened in {ctx.guild.name}\n in command {ctx.command}, which was run by {ctx.author.name}[{ctx.author.id}]:\n{trace}')

    def log(self, guild_id, log_msg: str):
        with open('main-config.json', 'r') as f:
            config = json.load(f)
            logfile = config['LogFile']
        if guild_id == 0:
            print(f"[{datetime.datetime.now()}] [\033[1;31mGLOBAL-ERR-HANDLR\033[0;0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [GLOBAL-ERR-HANDLR]: " + log_msg + "\n")
        else:
            print(f"[{datetime.datetime.now()}] [{guild_id}] [\033[1;31mGLOBAL-ERR-HANDLR\033[0;0m]: " + log_msg)
            with open(f'{logfile}', 'a') as f:
                f.write(f"[{datetime.datetime.now()}] [{guild_id}] [GLOBAL-ERR-HANDLR]: " + log_msg + "\n")
        print("\n")

def setup(client):
    client.add_cog(CommandErrorHandler(client))
