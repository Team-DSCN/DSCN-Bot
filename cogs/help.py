"""
This Discord Bot has been made to keep the server of DSCN Label safe and make it a better place for everyone.

Copyright © 2020 DSCN Label with ItsArtemiz (Augadh Verma). All rights reserved.

This Software is distributed with the GNU General Public License (version 3).
You are free to use this software, redistribute it and/or modify it under the
terms of GNU General Public License version 3 or later.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of this Software.

This Software is provided AS IS but WITHOUT ANY WARRANTY, without the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

For more information on the License, check the LICENSE attached with this Software.
If the License is not attached, see https://www.gnu.org/licenses/

To contact us (DSCN Management), mail us at teamdscn@gmail.com
"""

import discord, json

from discord.ext import commands
from datetime import datetime


with open("utils/vars.json") as f:
    data = json.load(f)

colour=int(data['colour'],16)
footer=data['footer']

class CustomHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'help':'Shows the help message',
            'aliases':['h', 'commands'],
            'usage':'[command]'
        })

    def get_command_signature(self, command:commands.Command):
        return f"{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", colour=colour, timestamp=datetime.utcnow())
        embed.description = f"Type {self.context.prefix}help command for more info on a command"
        embed.set_footer(text=footer)
        for cog, cmds in mapping.items():
            if cog and len(cmds) != 0:
                filtered = await self.filter_commands(cmds, sort=True)
                if len(filtered) != 0:
                    embed.add_field(name=cog.qualified_name, value=", ".join(f"`{c.name}`" for c in filtered), inline=False)
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=f"Help", colour=colour, timestamp=datetime.utcnow())
        embed.set_footer(text="<> - Required | [] - Optional")
        embed.description = f"**{group.qualified_name}**: {group.help if group.help else 'No help provided..'}"
        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            embed.add_field(name="Subcommands", value=", ".join(f"`{c.name}`" for c in filtered), inline=False)
                
        if len(group.aliases) != 0:
            embed.add_field(name="Aliases", value=", ".join(f"`{c}`" for c in group.aliases), inline=False)

        embed.add_field(name="Usage", value=f"`{self.context.prefix}{group.qualified_name} {group.signature}`" if group.signature else f"`{self.context.prefix}{group.qualified_name}`", inline=False)

        await self.get_destination().send(embed=embed)

    send_command_help = send_group_help

    async def send_cog_help(self, cog):
        embed = discord.Embed(title="Help", colour=colour, timestamp=datetime.utcnow())
        embed.set_footer(text=footer)
        if cog.description:
            embed.description = cog.description
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        embed.add_field(name=cog.qualified_name, value=", ".join(f"`{c.name}`" for c in filtered))
        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", colour=discord.Color.red(), timestamp=datetime.utcnow())
        embed.description = str(error)
        embed.set_footer(text=footer)
        await self.get_destination().send(embed=embed)




class MyHelp(commands.Cog, name="Help"):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        bot.help_command = CustomHelp()

def setup(bot:commands.Bot):
    bot.add_cog(MyHelp(bot))