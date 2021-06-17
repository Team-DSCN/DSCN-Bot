from __future__ import annotations
from typing import Optional, Union

import discord

from discord.ext import commands

class ArtistAdd(commands.FlagConverter, case_insensitive=True):
    name: str
    music: str = commands.flag(name='music', aliases=['style'])
    playlist: str = commands.flag(name='playlist', aliases=['list'])
    avatar: Optional[Union[discord.User, str]] = commands.flag(default=lambda ctx: ctx.guild.icon.url)

class ArtistEdit(commands.FlagConverter, case_insensitive=True):
    name: Optional[str]
    music: Optional[str]
    playlist: Optional[str]
    avatar: Optional[Union[discord.User, str]] = commands.flag(default=lambda ctx: ctx.guild.icon.url)