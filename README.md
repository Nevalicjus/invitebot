## Invitebot
A simple discord.py bot that connects invites to roles, and adds then on_member_join

## Using

If you want to use the bot 'out of the box', I host it publically [here](https://discord.com/api/oauth2/authorize?client_id=788044126242603070&permissions=268487921&scope=bot)

### If you want to selfhost:

  1. Clone the Bot
  2. Create a bot application on [Discord Developer Website](https://discord.com/developers)
  3. Go to config.json and fill the DiscordToken.
  4. If you want to host it for more than one server, I advise adding your Discord User ID to OwnerUsers in the config.json file.
  5. If you want to change the prefix/logfile name/if bot should delete owner command invocations change it in the config.json also.
  6. Add the bot to your server/servers. I advise giving him at least these permissions:
     - Manage Server
     - Manage Roles
     - Manage Channels
     - Create Invite
     - View Audit Log
     - Read Messages
     - Send Messages
     - Embed Links
     - Attach Files
     - Add Reactions
     or just the Administrator Permission.
     You should see files with server ids' appear in the configs/ directory.
  7. Move the bot above the roles you want to give on invites.
  8. Setup the invites.

Invites for the specific servers will be listed in the 'config files', under Invites.
If the bot falls out of sync with uses for certain invite, he should correct himself on the next member - member x - but rememebr, then the member x can have a misgiven role.
If you enable log, which isn't enabled on default, the bot will log some of his actions onto a discord channel.
If you add any Admin Roles, they will appear under General > AdminRoles.
If you choose to Delete Invocations on normal commands, it is sever specific and can be found under General > DeleteInvocations  

The bot prints it's actions on the console, and also writes them to a file 'log.txt', so you can view them later.

### Thanks
Great thanks to Piotr Młynarski
