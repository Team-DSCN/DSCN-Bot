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

from __future__ import annotations
import aiohttp

import discord

from typing import Iterable
from discord.ext import commands
from utils.context import Context

DESCRIPTION = """
Hello World! I am a bot written by ItsArtemiz#8858 to provide some utilities.
"""

ALLOWEDMENTIONS = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=False,
    replied_user=True
)

async def get_pre(bot: Bot, message:discord.Message) -> Iterable[str]:
    user_id = bot.user.id
    base = [f'<@{user_id}>', f'<@!{user_id}>']
    if message.guild is None:
        base.append('.')
    else:
        base.extend(await bot.utils.find_one({'name':'prefixes'}))
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
        
    async def get_context(self, message:discord.Message, *, cls=Context):
        return await super().get_context(message, cls=cls)
        
    async def create_session(self) -> None:
        await self.wait_until_ready()
        if not hasattr(self, 'session'):
            self.session = aiohttp.ClientSession()