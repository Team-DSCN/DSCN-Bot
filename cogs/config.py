# -*- codingL utf-8 -*-

"""
Configuration Module
~~~~~~~~~~~~~~~~~~~~~

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

import discord

from discord.ext import commands, tasks
from bot import DSCN, extensions
from random import choice
from utils.checks import staff

class Config(commands.Cog):
    """ Configuration Module """
    def __init__(self, bot:DSCN):
        self.bot = bot
        self.change_pres.start()

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx:commands.Bot, *, name:str):
        if name == "all":
            for f in extensions:
                try:
                    self.bot.reload_extension(f)
                except Exception as e:
                    await ctx.send(f"```py\n{e}```")
            return await ctx.reply("Reloading extensions successfull.")

        else:
            try:
                self.bot.reload_extension(f"cogs.{name}")
            except Exception as e:
                return await ctx.send(f"```py\n{e}```")
            await ctx.reply(f"Successfully reloaded: **`cogs/{name}.py`**")

    @commands.is_owner()
    @commands.command()
    async def load(self, ctx:commands.Context, *,name:str):
        """Loads a cog."""
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📥 Loaded extension: **`cogs/{name}.py`**")

    @commands.is_owner()
    @commands.command()
    async def unload(self, ctx:commands.Context, *,name:str):
        """Unloads a cog."""
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📤 Unloaded extension: **`cogs/{name}.py`**")


    async def get_activity(self) -> discord.Activity:
        from utils.songs import songs
        activity =  choice(songs)

        return discord.Activity(
            type = discord.ActivityType.listening,
            name = activity
        )

    def get_status(self) -> discord.Status:
        return choice([
            discord.Status.online,
            discord.Status.dnd,
            discord.Status.idle
        ])

    @tasks.loop(minutes=7.0)
    async def change_pres(self):
        status = self.get_status()
        activity = await self.get_activity()

        await self.bot.change_presence(
            activity=activity,
            status=status
        )

    @change_pres.before_loop
    async def before_change_pres(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.change_pres.cancel()


    @staff()
    @commands.group(invoke_without_command=True)
    async def status(self, ctx:commands.Context):
        if ctx.subcommand_passed is None:
            return await ctx.send_help(ctx.command)
    
    @staff()
    @status.command(name="add")
    async def _add(self, ctx:commands.Context, *, name:str):
        """ Add a song to be displayed in status. """
        from utils.songs import songs

        if name not in songs:
            songs.append(name)
            return await ctx.send("Added successfully")
        else:
            return await ctx.send(f"{name} already in songs.")

    @staff()
    @status.command()
    async def remove(self, ctx:commands.Context, *, name:str):
        """ Removes a song in the status list. """
        from utils.songs import songs
        try:
            songs.remove(name)
            return await ctx.send("Successfully removed")
        except ValueError:
            return await ctx.send("The song doesn't seems to be in the songs list.")

    @staff()
    @status.command(name="list")
    async def _list(self, ctx:commands.Context):
        """ Lists all the status in the songs list. """
        from utils.songs import songs

        embed = discord.Embed(
            colour=0x2F3136,
            description = ", ".join([f"`{s}`" for s in songs])
        )

        return await ctx.send(embed=embed)
        
def setup(bot:DSCN):
    bot.add_cog(Config(bot))