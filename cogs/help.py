"""
The bot's help command.
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
from utils.context import Context

import discord

from discord.ext import commands
from typing import List, Mapping, Optional, TYPE_CHECKING
from utils.utils import command_help
from utils.bot import Bot

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        
        self.verify_checks = False
        self.show_hidden = False
        
        super().__init__(
            command_attrs={
                'help':'Shows help for a command',
                'usage':'[command]'
            }
        )
        
    def get_command_signature(self, command: commands.Command | commands.Group) -> str:
        
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = ' | '.join(command.aliases)
            fmt = f'[{command.name} | {aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'
    
    
    async def send_bot_help(
        self,
        mapping: Mapping[Optional[commands.Cog], List[commands.Command]]
    ):
        """The main help command."""
        
        embed = discord.Embed(
            title='Help',
            colour=self.context.bot.colour,
            timestamp=discord.utils.utcnow()
            
        )
        embed.set_footer(text=self.context.bot.branding)
        can_run = 0
        _all = 0
        for cog, cmds in mapping.items():
            if cog and cmds:
                L = []
                for cmd in cmds:
                    if cmd.hidden:
                        pass
                    
                    else:
                        _all+=1
                        try:
                            await cmd.can_run(self.context)
                            can_run+=1
                            L.append(f'`{cmd.name}`')
                        except:
                            L.append(f'~~`{cmd.name}`~~')
                if L:                  
                    embed.add_field(
                        name=cog.qualified_name,
                        value=f', '.join(L),
                        inline=False
                    )
        
        embed.description = (
                f'Type `{self.context.clean_prefix}help [command]` for more info on a command.\n'\
                f'Commands that are striked, (i.e. ~~name~~) cannot be used by you.\n'\
                f'*You can run {can_run}/{_all} commands.*'
            )
        
        await self.get_destination().send(embed=embed)
        
    async def send_command_help(self, command: commands.Command | commands.Group):
        # Well, since making a single command for both Command and Group work so here it is.
        embed = discord.Embed(
            title=self.get_command_signature(command),
            description=command_help(command),
            timestamp=discord.utils.utcnow(),
            colour=self.context.bot.colour
        )
        embed.set_footer(text=self.context.bot.branding)

            
        if isinstance(command, commands.Group):
            L = []
            for cmd in command.commands:
                if TYPE_CHECKING:
                    cmd: commands.Command | commands.Group
                if cmd.hidden:
                    pass
                else:
                    try:
                        await cmd.can_run(self.context)
                        L.append(f'`{cmd.name}`')
                    except:
                        L.append(f'~~`{cmd.name}`~~')
            if L:
                embed.add_field(
                    name='Subcommands',
                    value=', '.join(L),
                    inline=False
                )
        try:
            await command.can_run(self.context)
            can_run = True
        except:
            can_run = False
        
        embed.add_field(
            name='Can Run?',
            value=f'{"Yes" if can_run else "No"}'
        )
        
        await self.get_destination().send(embed=embed)
    
    send_group_help = send_command_help
                    
    async def send_error_message(self, error):
        pass
    
class MyHelp(commands.Cog):
    """The bot's actual help command."""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bot.help_command = CustomHelp()
        
def setup(bot: Bot):
    bot.add_cog(MyHelp(bot))