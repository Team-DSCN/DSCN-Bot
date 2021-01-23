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

import traceback, aiohttp
import discord, json

from discord.ext import commands
from datetime import datetime

with open("utils/vars.json") as f:
    data = json.load(f)

footer = data['footer']
LogChannel = data['channels']['LogChannel']

class ErrorHandler(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    async def mystbin(self, data):
      data = bytes(data, 'utf-8')
      async with aiohttp.ClientSession() as cs:
        async with cs.post('https://mystb.in/documents', data = data) as r:
          res = await r.json()
          key = res["key"]
          return f"https://mystb.in/{key}.py"

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        shh = (
            commands.CommandNotFound,
            commands.NotOwner,
            commands.MissingPermissions,
            commands.CheckFailure
        )
        
        handler = (
            commands.MissingRequiredArgument,
            commands.BadArgument,
            commands.BotMissingPermissions,
            commands.CommandOnCooldown,
            commands.PrivateMessageOnly,
            commands.NoPrivateMessage,
            discord.NotFound,
            commands.TooManyArguments,
            commands.CheckAnyFailure
        )

        if isinstance(error, shh):
            return
        elif isinstance(error, handler):
            await ctx.send(embed = discord.Embed(title="Error",description=str(error), colour=discord.Color.red(),timestamp=datetime.utcnow()).set_footer(text=footer))
        else:
            tb ="".join(traceback.format_exception(type(error), error, error.__traceback__))
            try:
                embed = discord.Embed(
                    description = f"```py\n{tb}```",
                    colour=discord.Colour.red(),
                    title="An unexpected error occured",
                    timestamp=datetime.utcnow()
                )
                embed.set_footer(text=f"Caused by command: {ctx.command}")

                await ctx.send(embed=embed)
            except:
                err = await self.mystbin(tb)
                embed = discord.Embed(
                    title="An unexpected error occured",
                    timestamp=datetime.utcnow(),
                    colour=discord.Colour.red(),
                    description=f"The error is too long to send.\nHere, I have uploaded the error to [MystBin]({err}).",
                    url=err
                )
                embed.set_footer(text=f"Caused by command: {ctx.command}")
                await ctx.send(embed=embed)
            raise error
def setup(bot:commands.Bot):
    bot.add_cog(ErrorHandler(bot))