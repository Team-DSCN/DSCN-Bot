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

import json, aiohttp
from discord.ext import commands

# getting data from the json

with open("utils/vars.json") as f:
    data = json.load(f)

TestChannel = data['channels']['TestChannel']
BotCommands = data['channels']['BotCommands']
LogChannel = data['channels']['LogChannel']

owners = (449897807936225290, 488012130423930880, 393378646162800640)

class Checks:
    def botcmdchannel(self):
        def predicate(ctx:commands.Context):
            return (ctx.channel.id == TestChannel or ctx.channel.id == BotCommands)
        return commands.check(predicate)

    def botorowner(self):
        def predicate(ctx:commands.Context):
            return (ctx.channel.id == TestChannel or ctx.channel.id == BotCommands or ctx.author.id in owners)
        return commands.check(predicate)

    def everythingDM(self):
        """Checks for:
        → Set bot channel
        → Set owners
        → Is Dm
        """
        def predicate(ctx:commands.Context):
            return (ctx.channel.id == TestChannel or ctx.channel.id == BotCommands or ctx.author.id in owners or ctx.guild is None)
        return commands.check(predicate)





class Requests:
    async def get(self, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(*args, **kwargs) as r:
                json_object = await r.json()

                return {"status":r.status, "json":json_object}