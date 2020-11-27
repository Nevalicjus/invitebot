## Invitebot
A simple discord.py bot that connects invites to roles, and adds then on_member_join

## How to
I didn't add a viaDiscord way of setting it up, so you have to do it manually
Go to config.json and fill the DiscordToken slot
If you want to make changes to the names of files, or change the prefix the bot uses, you can do it there too

- Setup a bot application on [Discord Developer Website](https://discord.com/developers)
- Add the bot to your server
- Move the bot's role bove the role's you want to be able to add on_join
- Setup the invites.
You don't need to fill the uses file, but you need to 'complete' the invites file, or it's going to give errors as it doesn't know the invites a member uses
The way they are written there is pretty modular;

``{\n
  "Invite_Code": {\n
  "role1": "Role_Name",\n
  "role2": "Role_Name"\n
  },\n
  "Invite_Code: {\n
  "role1": "Role_Name",\n
  "role2": "Role_Name"\n
  }\n
}``

There is *theoreticallly* no limit to the amount of roles added on one invite, and invite codes you can add
Remember about commas
The names of the keys (role1, role2, role3 etc.) don't really matter, they're just there to be there

The bot prints on the console it's actions, and also writes them to a file 'log.txt', so you can view them later.

### Thanks
Great thanks to Piotr Młynarski who donated large part of the code to me
