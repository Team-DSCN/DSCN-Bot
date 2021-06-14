"""
The Context of the bot.
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

from utils.bot import Bot
from typing import Optional
from discord.ext import commands

class Context(commands.Context):
    bot: Bot
    
    def __init__(self, **attrs):
        super().__init__(**attrs)
        
    def __repr__(self) -> str:
        return f'<Context>'
    
    @property
    def session(self) -> aiohttp.ClientSession:
        return self.bot.session
    
    def tick(self, opt:Optional[bool], label=None) -> str:
        lookup = {
            True:'<:yesTick:818793909982461962>',
            False:'<:noTick:811230315648647188>',
            None:'<:maybeTick:853693562113622077>'
        }
        
        emoji = lookup.get(opt, '<:noTick:811230315648647188>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji
    
    async def thumbsup(self) -> None:
        try:
            return await self.message.add_reaction('\N{THUMBS UP SIGN}')
        except discord.HTTPException:
            pass
