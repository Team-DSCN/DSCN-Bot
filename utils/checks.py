# -*- codingL utf-8 -*-

"""
Checks
~~~~~~~

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

from discord.ext import commands
from .errors import NotBotChannel, InvalidArtist, NotStaff

AR = 820579878826278932
STAFF = 781796816257548308
ARTIST = 782673506483568670
BOTCHANNEL = 781809910823518218

def staff():
    async def pred(ctx:commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        elif STAFF in [r.id for r in ctx.author.roles]:
            return True
        else:
            raise NotStaff(f"{ctx.author} is not a member of the staff team.")
    return commands.check(pred)

def ar():
    async def pred(ctx:commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        elif STAFF in [r.id for r in ctx.author.roles]:
            return True
        elif AR in [r.id for r in ctx.author.roles]:
            return True
        else:
            raise NotStaff(f"{ctx.author} is not a member of the A&R team.")

    return commands.check(pred)

def artist():
    async def pred(ctx:commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        elif STAFF in [r.id for r in ctx.author.roles]:
            return True
        elif ARTIST in [r.id for r in ctx.author.roles]:
            return True
        else:
            raise InvalidArtist(f"{ctx.author} is not a registered artist.")
    return commands.check(pred)

def bot_channel():
    async def pred(ctx:commands.Context):
        if await ctx.bot.is_owner(ctx.author):
            return True
        elif STAFF in [r.id for r in ctx.author.roles]:
            return True
        elif ctx.channel.id == BOTCHANNEL:
            return True
        else:
            raise NotBotChannel("This command can be used only in a bot channel.")

    return commands.check(pred)