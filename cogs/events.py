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

LogChannel = data['channels']['LogChannel']
colour = data['colour']

class DiscordEvents(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.LogChannel = self.bot.get_channel(LogChannel)
        if self.LogChannel is None:
            self.LogChannel = self.bot.get_channel(789191146647322624)

    @commands.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        """
        Logs an edited message in the log channel. The message must be in the internal cache to be logged.
        """
        if before.content != after.content:
            if not before.author.bot:
                embed = discord.Embed(title="Message Edited", colour=0xb7e87e, timestamp=after.edited_at)
                embed.description = f"Edited in {before.channel.mention} | [Jump to message]({after.jump_url})"
                embed.add_field(name="Before", value=before.content, inline=False)
                embed.add_field(name="After", value=after.content, inline=False)
                embed.set_footer(text="Edited at")
                embed.set_author(name=str(before.author), icon_url=before.author.avatar_url)
                await self.LogChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        """
        Logs the message deleted in the log channel. The message must be in the internal cache to be logged.
        """
        if not message.author.bot:
            embed = discord.Embed(title="Message Deleted", colour=0x284f8c, timestamp=datetime.utcnow())
            embed.description = f"Deleted in {message.channel.mention}"
            embed.add_field(name="Content", value=message.content)
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            embed.set_footer(text="Deleted at")
            await self.LogChannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        """
        Logs when a member leaves the server. The member doesn't need to be in the internal cache because this fires when the member leaves.
        """
        embed = discord.Embed(title="Member Left", colour=discord.Color.dark_red(), timestamp=datetime.utcnow())
        embed.description = f"{member.mention} ({str(member)} [{member.id}]) has left us."
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=str(member.author), icon_url=member.avatar_url)
        embed.set_footer(text="Left at")
        await self.LogChannel.send(embed=embed)
        

def setup(bot:commands.Bot):
    bot.add_cog(DiscordEvents(bot))