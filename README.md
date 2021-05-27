<a target="https://n3v.live/invitebot" href="https://n3v.live/invitebot"><img src="https://n3v.live/icons/bot-invite-blue.svg"></a>
<a href="https://discord.gg/wsEU32a3ke"><img alt="Discord" src="https://img.shields.io/discord/788042409799712788?style=flat&logo=discord"></a>
<img src="https://n3v.live/icons/license-MIT-yellow.svg">
<a target="https://docs.n3v.live" href="https://docs.n3v.live"><img src="https://n3v.live/icons/read-the-docs-00BDD6.svg"></a>

# InviteBot
InviteBot is a simple discord.py bot that connects invites to roles, and adds then on_member_join

If you run into a bug please report it to me :)

## Usage
If you want to use the bot 'out of the box', I host it publically [here](https://n3v.live/invitebot).</br>
Be aware that as the bot is under developement, some issues can arise if you use the public version hosted by me (up to when it's 'finished').

### If you want to selfhost:
  1. Clone the Bot
  2. Create a bot application on [Discord Developer Website](https://discord.com/developers). Your bot application has to have Members Intent enabled, you can find this setting on the same page where the bot's token is.
  3. Go to [main-config.json](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json) and fill the [DiscordToken](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L2).
  4. If you want to host it for more than one server, I advise adding your Discord User ID to [OwnerUsers](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L5) in the config.json file.
  5. If you want to change the [prefix](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L3)/[logfile name](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L4)/[if bot should delete owner command invocations](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L6), change it in the config.json also.
  6. Start the bot (I've included [start.sh](https://github.com/Nevalicjus/invitebot/blob/main/start.sh) if you want to run it as a screen)
  7. Add the bot to your server/servers. I advise giving him at least these permissions:
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

     (so weight 268487921)
     or just the Administrator Permission (weight 8).
     You should see files with server ids' appear in the configs/ directory.
  8. Move the bot above the roles you want to give on invites.
  9. Setup the invites.

- Invites for the specific servers will be listed in the 'config files', under [Invites](https://github.com/Nevalicjus/invitebot/blob/main/configs/example.json#L7)

- If the bot falls out of sync with uses for certain invite, he should correct himself on the next member - member x - but rememeber, then the member x can have a misgiven role

- If you enable [log](https://github.com/Nevalicjus/invitebot/blob/main/configs/example.json#L5), which isn't enabled on default, the bot will log some of his actions onto a discord channel

- If you add any Admin Roles, they will appear under General > [AdminRoles](https://github.com/Nevalicjus/invitebot/blob/main/configs/example.json#L4)

- If you choose to Delete Invocations on normal commands, it is sever specific and can be found under General > [DeleteInvocations](https://github.com/Nevalicjus/invitebot/blob/main/configs/example.json#L3)  

The bot prints it's actions on the console, and also writes them to a [logfile](https://github.com/Nevalicjus/invitebot/blob/main/main-config.json#L4), so you can view them later

## Contributing
If you want to contribute, join the [discord server](https://discord.gg/wsEU32a3ke) and see **§ Contributing** on #info📜.

## Contact
You can contact me on Discord - find me on the [Support Server](https://discord.gg/wsEU32a3ke)/[Twitter](https://twitter.com/maciejbromirski)

## Thanks
Great thanks to Piotr Młynarski for the first version of the algorithm
