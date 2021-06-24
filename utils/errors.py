"""
Some external errors
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

from discord.ext import commands

class CollectionNotSet(Exception):
    pass

class NotBotChannel(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if not message:
            message = (
                'The current channel is not whitelisted.'\
                ' Use the commands in a channel that is whitelisted.'
            )
        else:
            message = message
        super().__init__(message=message, *args)