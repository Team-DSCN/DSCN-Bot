# -*- codingL utf-8 -*-

"""
Help Command Module
~~~~~~~~~~~~~~~~~~~~

This file replaces the default help command.

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

from typing import List, Mapping, Union
from discord.ext import commands
from datetime import datetime

class HelpSource(commands.HelpCommand):
    def __init__(self, **options):
        self.colour = options.pop('colour', discord.Color.from_rgb(49, 255, 200))
        self.footer = options.pop('footer', 'DSCN')

        self.verify_checks = True
        self.show_hidden = False
        super().__init__(
            command_attrs={
                "help":"Lists all the top notch commands based on your permission level <:rooEz:821814613124579339>",
                "usage":"[command]"
            }
        )

    def command_usage(self, cmd:Union[commands.Command, commands.Group]) -> str:
        return f"{cmd.qualified_name} {cmd.signature}"

    def command_help(self, cmd:Union[commands.Command, commands.Group]) -> str:
        return cmd.help if cmd.help else 'No help provided...'

    async def send_bot_help(
        self,
        mapping
    ):

        """
        The bot's help command.
        """
        embed = discord.Embed(
            title="Help",
            colour = self.colour,
            timestamp=datetime.utcnow(),
            description=f"Type `{self.clean_prefix}help [command/category]` for more info on a command or a category."
        ).set_footer(text=self.footer)

        for cog, cmds in mapping.items():
            if cog and cmds:
                f = await self.filter_commands(cmds, sort=True)
                if f:
                    try:
                        embed.add_field(
                            name=cog.qualified_name,
                            value=f", ".join([f"`{c.name}`" for c in f]),
                            inline=False
                        )
                    except:
                        pass
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command:Union[commands.Command, commands.Group]):
        """
        I am just using `send_command_help` because I am lazy and it works.
        """
        embed = discord.Embed(
            title="Help",
            description=self.command_help(command),
            colour=self.colour,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=self.footer)

        embed.add_field(
            name="Usage",
            value=f"`{self.command_usage(command)}`",
            inline=False
        )

        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join([f"`{c}`" for c in command.aliases]),
                inline=False
            )

        if isinstance(command, commands.Group):
            f = await self.filter_commands(command.commands, sort=True)
            embed.add_field(
                name="Subcommands",
                value=", ".join([f"`{c.name}`" for c in f]),
                inline=False
            )

        await self.get_destination().send(embed=embed)

    send_group_help = send_command_help


    async def send_cog_help(self, cog:commands.Cog):
        """
        This sends the help regarding an extension.
        """

        embed = discord.Embed(
            title = f"All the commands for `{cog.qualified_name}` category",
            colour = self.colour,
            timestamp = datetime.utcnow()
        ).set_footer(text=self.footer)

        if cog.description:
            embed.description = cog.description
        
        f = await self.filter_commands(cog.get_commands(), sort=True)
        for cmd in f:
            try:
                embed.add_field(
                    name = self.command_usage(cmd),
                    value = self.command_help(cmd)
                )
            except:
                pass

        await self.get_destination().send(embed=embed)

class Help(commands.Cog):
    """
    RoboArt's help command!
    """

    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.bot.help_command = HelpSource()

def setup(bot:commands.Bot):
    bot.add_cog(Help(bot))