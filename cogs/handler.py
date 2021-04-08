# -*- codingL utf-8 -*-

"""
Error Handler Module
~~~~~~~~~~~~~~~~~~~~

This file is responsible for handling command_invoke_error.

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
import traceback, sys

from discord.ext import commands
from discord.ext.commands.errors import CommandOnCooldown
from utils.channel_logging import post_log, embed_builder

class ErrorHandler(commands.Cog):
    """
    An error handler. Not much to say here.
    """
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx:commands.Context, error:commands.CommandError):
        """The event triggered when an error is raised while invoking a command.
        
        Parameters
        ----------
        ctx: Context
            The context used for invoking the command.
        error: CommandError
            The :class:`Exception` raised.
        """
        error = getattr(error, 'original', error)

        if hasattr(ctx.command, 'on_error'):
            return #This prevents commmands with local error handlers to be handled here.

        ignored = (commands.CommandNotFound,)

        # This will ignore the Exceptions in the ignored tuple.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.MissingPermissions):
            embed = embed_builder(
                bot=self.bot,
                title = "Missing Permissions <:rooPopcorn:821814611837321226>",
                description=str(error),
                user = ctx.author,
                colour = discord.Colour.red()
            )

            await ctx.send(embed = embed)

        elif isinstance(error, commands.BotMissingPermissions):
            embed = embed_builder(
                bot = self.bot,
                title = "I am missing some permissions <:rooPopcorn:821814611837321226>",
                description=str(error),
                user = self.bot.user
            )

            try:
                await ctx.send(embed=embed)
            except:
                await ctx.send(str(error))

        elif isinstance(error, CommandOnCooldown):
            embed = embed_builder(
                bot = self.bot,
                title=f"Command `{ctx.command}` is on cooldown <:rooPopcorn:821814611837321226>",
                description = str(error),
                user = ctx.author
            )

            await ctx.send(embed = embed)

        elif isinstance(error, commands.NotOwner):
            embed = embed_builder(
                bot = self.bot,
                title = f"Command `{ctx.command}` is owner only <:pepepoint:821814611699433533>",
                description=str(error),
                user = ctx.author
            )

            await ctx.send(embed=embed)

        elif isinstance(error, (commands.MemberNotFound, commands.UserNotFound)):
            embed = embed_builder(
                bot = self.bot,
                title = "Unable to locate the user <:notlikeduck:822817257583280149>",
                description = str(error),
                user = ctx.author
            )

            await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Invalid command usage, follow the help:")
            await ctx.send_help(ctx.command)
        else:
            embed = embed_builder(
                bot = self.bot,
                title = "An Unexpected Error Occurred",
                description=str(error),
                user=ctx.author,
                colour= discord.Colour.red(),
                footer=f"Caused by: {ctx.command}"
            )

            await ctx.send(embed = embed)
            msg = await post_log(ctx.guild, name="bot-logs", embed=embed)
            await msg.pin(reason="An unexpected error occurred")

            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    
def setup(bot:commands.Bot):
    bot.add_cog(ErrorHandler(bot))