# DSCN

![DSCN](https://media.discordapp.net/attachments/781811569378066452/852956080929767425/20210115_002051_0000.png?width=750&height=120)

A discord bot made for the label [DSCN](https://www.youtube.com/channel/UChzJhEHSJcG2-lg9Y5vNgNA)'s [Discord](https://discord.gg/2NVgaEwd2J) Server.

## Inviting the bot

The bot currently is in "Testing" mode and is not available to the public at the moment. Join our [Discord](https://discord.gg/2NVgaEwd2J) Server to stay updated about the bot.

## Configuring the bot

Even though the bot isn't out to the public yet, I'll still mention on how to configure the bot when you invite it to your server.

Upon inviting, the bot's prefix by default is `.` (a fullstop). The bot is still completely useful but I have integrated a few features which will help server owners in setting up the bot according to their needs.

Starting of, you will have to run the command `.setup` so that your guild (server) is registered with us in our database. Now you can configure the following:

- Bot prefixes (you can have more than one prefix)
- Log channel (The bot will log quite a bit of stuff like member join/leave etc)
- Blacklist channels (in these channels, users won't be able to use bot commands)

**NOTE: Anyone with the MANAGE GUILD permissions can configure the bot.**

### Managing Prefix

To manage your guild's prefixes, you have to use the command:

- Adding a prefix is simple as: `.settings prefix add ?` (This will add `?` as one of the bot's prefixes)

- Removing a prefix: `.settings prefix remove ?` (This will remove `?` from the bot's prefix)

### Managing Log Channel

- To set up a log channel, use the command `.settings log #channel`

    This will set `#channel` as a logs channel for logging various stuff.

- If you want to remove a log channel, run `.settings log`

    This will remove the set log channel for your guild.

### Managing Blacklisted Channels

To enable/disable commands in a channel, run the command: `.settings commands enable/disable` in the channel

You may also provide a channel while running the command: `.settings commands #channel enable/disable`

Note: It is either `enable` or `disable` depending upon whether you want to enable or disable the commands.

## Viewing Your Settings

To view your settings, run `.settings`

## Running

The bot is being hosted on `python 3.9.5` but a minimum of `python 3.8` is required.

The [discord.py](https://github.com/Rapptz/discord.py) library being used is "in dev", i.e. I am fetching from the `master` branch of the library which is obviously unstable.

### Installing dependencies

- All the requirements can be found in `requirements.txt` file

### Creating a Database

- The DSCN Bot is using the [MongoDB](https://mongodb.com/) database. You will need to create an account on MongoDB to use this.

### Configuring Environments

- Create a `.env` file and add the following:

```yaml
BOT_TOKEN=<Your Bot Token>
DB_TOKEN=<MongoDB URI>

TECH_API_KEY=<The API Key being used for fetching news>
TECH_NEWS_LOGGER=<The discord webhook url to a channel to post the news in>

DSCN_LOGGER=<The discord webhook url to a channel to post guild join logs>
```

Note: `<>` shouldn't be used.

## Disclaimer

### License

This piece of software comes with [GNU General Public License V3](https://www.gnu.org/licenses/)

Check [LICENSE](https://github.com/Team-DSCN/DSCN-Bot/blob/main/LICENSE) for more info.

### Self Hosting

Self-hosting is not encouraged and won't be helped with. This is here for educational purposes. If you want an instance of the bot, please invite it [here](https://discord.com/oauth2/authorize?client_id=788766967472979990&scope=bot&permissions=8).

## Contributing

In order to contribute to this project, you can make a PR to the `dev` branch of this repo. PRs to the `main` branch will be straight up rejected. Also make sure you test your code before making the PR!

## Links

Mail us at [teamdscn@gmail.com](mailto:teamdscn@gmail.com)

Join us ar our [Discord Server](https://discord.gg/2NVgaEwd2J)

Our [Spotify](https://open.spotify.com/playlist/4uLeZlMiJSvYjSsJMTKdDs?si=9b34a8470cce4ba3) playlist

[YouTube](https://www.youtube.com/c/DSCNrecords)
