# -*- codingL utf-8 -*-

"""
DSCN
~~~~~~

The main file responsible for initialising the bot.

Copyright (c) 2021 ItsArtemiz (Augadh Verma)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ItsArtemiz#8858 or https://discord.gg/2NVgaEwd2J

"""

from datetime import datetime
from utils.mongoclient import MongoClient
import discord
import aiohttp
import sys, traceback, os

from discord.ext import commands
from typing import Optional

from dotenv import load_dotenv
load_dotenv() #This is only required if you are self-hosting the bot, but this doesnt harm anything


# Just some jishaku stuff
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

# Prefixes
prefix = (";",".")

# Intial extensions to load.
extensions = (
    "cogs.event_logging",
    "jishaku",
    "cogs.handler",
    "cogs.help",
    "cogs.info",
    "cogs.tags",
    "cogs.tech",
    "cogs.config"
)


class DSCN(commands.Bot):
    def __init__(self ,*args, **kwargs):
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True, replied_user=True)
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=commands.when_mentioned_or(*prefix),
            intents=intents,
            allowed_mentions=allowed_mentions,
            case_insensitive=True,
            **kwargs
        )

        self.loop.create_task(self.create_session())
        self.colour = 0xce0037 #discord.Color.from_rgb(49, 255, 200) #Beta Colour
        
        self.version = "1.1.2"
        self.footer = "DSCN"

        for cog in extensions:
            try:
                self.load_extension(cog)
            except Exception as e:
                print(f"Failed to load extension {cog}.", file=sys.stderr)
                traceback.print_exc()

    async def create_session(self):
        """ Creates an aiohttp ClientSession and a db. """

        await self.wait_until_ready()
        if not hasattr(self, "session"):
            self.session = aiohttp.ClientSession()
        if not hasattr(self, "db"):
            self.db = MongoClient(db="DSCN", collection="Artists")
        if not hasattr(self, "tagdb"):
            self.tagdb = MongoClient(db="DSCN", collection="Tags")


    async def get_or_fetch_member(self, guild:discord.Guild, member_id:int) -> Optional[discord.Member]:
        """Searches the cache for a member or fetches if not found.
        
        Parameters
        -----------
        guild: Guild
            The guild where we will do the searching.
        member_id: int
            The member ID to search for.
            
        Returns
        --------
        Optional[Member]
            The member or None if not found
        """

        member = guild.get_member(member_id)
        if member:
            return member

        try:
            member = await guild.fetch_member(member_id)
        except discord.HTTPException:
            return None
        else:
            return member

    async def on_ready(self):
        print(f"{self.user} is up and now running! (ID: {self.user.id})")

        if not hasattr(self, "uptime"):
            self.uptime = datetime.utcnow()
    

if __name__ == "__main__":
    bot = DSCN()
    bot.run(os.environ.get("BOT_TOKEN"))