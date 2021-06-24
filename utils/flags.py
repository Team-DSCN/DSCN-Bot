"""
Flags in-concern with the bot
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
from typing import Optional, Union

import discord

from discord.ext import commands

class ArtistAdd(commands.FlagConverter, case_insensitive=True):
    name: str
    music: str = commands.flag(name='music', aliases=['style'])
    release: str = commands.flag(name='release', aliases=['playlist'])
    avatar: Optional[Union[discord.User, str]] = commands.flag(default=lambda ctx: ctx.guild.icon.url)

class ArtistEdit(commands.FlagConverter, case_insensitive=True):
    name: Optional[str]
    music: Optional[str]
    release: Optional[str]
    avatar: Optional[Union[discord.User, str]]
    aliases: Optional[str]