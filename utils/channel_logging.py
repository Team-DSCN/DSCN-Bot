# -*- codingL utf-8 -*-

"""
Channel Logging
~~~~~~~~~~~~~~~~~

This file logs various events.

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

from datetime import datetime
from typing import Optional, Union

from discord.ext import commands

from .errors import ChannelNotFound

async def post_log(guild:discord.Guild ,name:str=None, id:int=None, **kwargs) -> Optional[discord.Message]:
    """Logs in the channel given.

    Parameters
    -----------
    name: Optional[str]
        The name of the channel to find.
    id: Optional[int]
        The id of the channel to find.
    **kwargs: Keyword arguments for sending a message/log in the channel

    Returns
    --------
    Optional[Message]
        The message sent or ``None`` if unable to send.

    Raises
    -------
    ChannelNotFound
        If the channel wasn't found.
    discord.HTTPException
        Sending the message failed.
    discord.Forbidden
        You do not have proper permissions to send the message.
    discord.InvalidArgument
        The `files` list is not of the appropriate size, you specified both `file` and `files`, or the `reference` object is not a Message or MessageReference.
    """
    channel = None
    if name:
        channel = discord.utils.get(guild.text_channels, name=name)
        if not channel:
            raise ChannelNotFound(f"Channel '{name}' was not found in the guild channels.")
    elif id:
        channel = guild.get_channel(id)
        if not channel:
            raise ChannelNotFound(f"Channel with id {id} was not found in the guild channels.")

    return await channel.send(**kwargs)

def embed_builder(bot:commands.Bot, title:str, description:str, user:Union[discord.Member, discord.User], colour:discord.Colour=None, footer:str=None) -> discord.Embed:
        """Builds an embed.

        Parameters
        -----------
        bot: Bot
            The bot to be passed to get some default attributes.
        title: str
            The title of the embed.
        description: str
            The description of the embed.
        user: Union[Member, User]
            The user to be set for author field of embed.
        colour: Optional[Colour]
            An instance of :class:`Colour`. Can be derived from `Colour.from_rgb()`.
            If a colour is not provided, the colour property of the bot is used which was set while initialising it.
        footer: Optional[str]
            The footer to be set for embed.
            If the footer is not provided, the footer property of the bot is used which was set while initialsing it.

        Returns
        --------
        Embed
            The embed created.
        """
        colour = colour or bot.colour
        embed = discord.Embed(
            title=title,
            description = description,
            timestamp = datetime.utcnow(),
            colour = colour
        )
        embed.set_footer(text=footer or bot.footer)
        embed.set_author(name=str(user), icon_url=user.avatar_url, url=f"https://discord.com/users/{user.id}")

        return embed