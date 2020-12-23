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

import discord
import json
import os

from discord.ext import commands
from datetime import datetime


with open("utils/vars.json", "r") as f:
    data = json.load(f)
prefix = data['prefix']

intents = discord.Intents.all()

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_HIDE"] = "True"

bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True, intents=intents, allowed_mentions= discord.AllowedMentions(users=True, roles=True, everyone=True))

bot.owner_ids = (449897807936225290, 488012130423930880, 393378646162800640)
bot.start_time = datetime.utcnow()

@bot.event
async def on_ready():
    print("{0.user} is up and running".format(bot))

@bot.event
async def on_message(message:discord.Message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    if message.content.endswith('<@788766967472979990>'):
        await message.channel.send(f"My prefix is: {prefix}")
    if message.content.endswith('<@!788766967472979990>'):
        await message.channel.send(f"My prefix is: {prefix}")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension("cogs.{}".format(filename[:-3]))

bot.load_extension("jishaku")

bot.run(os.environ.get("BotToken"))