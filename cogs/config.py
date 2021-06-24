"""
Some Configs of the bot
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

import discord
import random

from typing import Any
from discord.ext import commands, tasks
from utils.bot import Bot
from utils.context import Context


class Config(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    def error(self, e: Any) -> str:
        return f'```py\n{e}```'
        
    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: Context, *, name: str):
        try:
            self.bot.load_extension(name)
        except Exception as e:
            return await ctx.send(self.error(e))
        await ctx.send(f'📥 `{name}`')
        
    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: Context, *, name: str):
        try:
            self.bot.unload_extension(name)
        except Exception as e:
            return await ctx.send(self.error(e))
        await ctx.send(f'📤 `{name}`')
        
    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: Context, *, name: str):
        if name == 'all':
            for cog in self.bot.cogs.keys():
                try:
                    self.bot.reload_extension(cog)
                except Exception as e:
                    await ctx.send(self.error(e))
            await ctx.send('\U0001f501 Reloaded all cogs')
            
        else:
            try:
                self.bot.reload_extension(name)
            except Exception as e:
                return await ctx.send(self.error(e))
            await ctx.send(f'\U0001f501 `{name}`')
            
            
    def status(self) -> discord.Status:
        return random.choice([
            discord.Status.online,
            discord.Status.offline,
            discord.Status.dnd
        ])
        
    async def get_activity(self, *, All=False) -> discord.Activity | list:
        pass
    
    @tasks.loop(minutes=5.0)
    async def status_loop(self) -> None:
        status = self.status()
        activity = await self.get_activity()
        
        await self.bot.change_presence(activity=activity, status=status)
    
    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()
                    

def setup(bot: Bot):
    bot.add_cog(Config(bot))