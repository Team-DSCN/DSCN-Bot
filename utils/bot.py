"""
Subclass of commands.Bot
Copyright (C) 2021  ItsArtemiz (Augadh Verma)

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
"""

import aiohttp
import discord
import os

from typing import Iterable, List, Optional
from datetime import datetime
from discord.ext import commands
from utils.db import Client
from dotenv import load_dotenv
load_dotenv()

DESCRIPTION = """
Hello World! I am a bot written by ItsArtemiz#8858 to provide some utilities.
"""

URI = os.environ.get('DB_TOKEN')
TOKEN = os.environ.get('BOT_TOKEN')

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

ALLOWEDMENTIONS = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=False,
    replied_user=True
)

EXTENSIONS = {
    'jishaku',
    'cogs.artists'
}

async def get_pre(bot, message:discord.Message) -> Iterable[str]:
    user_id = bot.user.id
    base = [f'<@{user_id}>', f'<@!{user_id}>']
    if message.guild is None:
        base.append('.')
    else:
        try:
            prefixes:List = (await bot.utils.find_one({'name':'prefixes'}))[message.guild.id]
        except (TypeError, KeyError, AttributeError):
            base.append('.')
        else:
            base.extend(prefixes)
    return base

class Bot(commands.Bot):
    """The actual robot!!"""
    
    def __init__(self) -> None:
        intents = discord.Intents.all()
        
        super().__init__(
            command_prefix=get_pre,
            description=DESCRIPTION,
            allowed_mentions=ALLOWEDMENTIONS,
            intents=intents,
            owner_id=449897807936225290,
            case_insensitive=True,
            strip_after_prefix=True
        )
        
        self.loop.create_task(self.create_session())

        self.colour = 0xce0037
        self.branding = 'DSCN'
        self.version = '1.2.0'
        
        for extension in EXTENSIONS:
            self.load_extension(extension)
    
        
    async def get_context(self, message:discord.Message, cls=None):
        # circular import, thanks python
        from utils.context import Context
        return await super().get_context(message, cls=Context)
        
    async def create_session(self) -> None:
        await self.wait_until_ready()
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()
        if not hasattr(self, 'artists'):
            self.artists = Client(URI, 'DSCN', 'Artists')
        # if not hasattr(self, 'tags'):
        #     self.tags = Client(URI, 'DSCN', 'Tags')
        # if not hasattr(self, 'utils'):
        #     self.utils = Client(URI, 'DSCN', 'Utils')

    async def on_ready(self) -> None:
        print(f'READY: {self.user} (ID:{self.user.id})')

        if not hasattr(self, 'uptime'):
            self.uptime = datetime.utcnow()
            
    def run(self, *args, **kwargs):
        return super().run(TOKEN, *args, **kwargs)