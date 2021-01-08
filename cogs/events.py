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

colour = data['colour']

class DiscordEvents(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

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
                try:
                    LogChannel = discord.utils.get(before.guild.text_channels, name="bot-logs")
                    await LogChannel.send(embed=embed)
                except:
                    pass

    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        if not message.author.bot:
            embed = discord.Embed(title="Message Deleted", colour=16764416, timestamp=message.created_at)
            embed.description = f"Deleted in {message.channel.mention}"
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            embed.set_footer(text="Deleted at")
            embed.add_field(name="Content", value=message.content)
            try:
                LogChannel = discord.utils.get(message.guild.text_channels, name="bot-logs")
                await LogChannel.send(embed=embed)
            except:
                pass


    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        embed = discord.Embed(title="Member Left", colour=discord.Color.red(), timestamp=datetime.utcnow())
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.add_field(name="Joined us at", value=datetime.strftime(member.joined_at, '%a %d, %B of %Y at %H:%M%p'))
        if len(member.roles)>0:
            embed.add_field(name="Roles", value=", ".join([role.mention for role in member.roles]))
        embed.set_footer(text=f"ID: {member.id}")
        try:
            LogChannel = discord.utils.get(member.guild.text_channels, name="bot-logs")
            await LogChannel.send(embed=embed)
        except:
            pass


    @commands.Cog.listener()
    async def on_member_update(self, before:discord.Member, after:discord.Member):
        if not before.bot:
            embed=discord.Embed(title="Member Update", colour=before.colour,timestamp=datetime.utcnow())
            if before.nick != after.nick:
                embed.set_footer(text="Updated at")
                embed.set_author(name=str(before), icon_url=before.avatar_url)
                embed.add_field(name="Before", value=before.nick, inline=False)
                embed.add_field(name="After", value=after.nick)

            if before.roles != after.roles:
                embed.set_footer(text="Updated at")
                embed.set_author(name=str(before), icon_url=before.avatar_url)
                temp = list(set(before.roles + after.roles))
                added = []
                removed = []
                for role in temp:
                    if role in before.roles and role not in after.roles:
                        added.append(role)
                    elif role in after.roles and role not in before.roles:
                        removed.append(role)
                if len(added)>0:
                    embed.add_field(name="Roles Added", value=", ".join([r.mention for r in added]),inline=False)
                if len(removed)>0:
                    embed.add_field(name="Roles Removed", value=", ".join([r.mention for r in removed]), inline=False)

            try:
                LogChannel = discord.utils.get(before.guild.text_channels, name="bot-logs")
                await LogChannel.send(embed=embed)
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        if not member.pending:
            embed = discord.Embed(title=f"Welcome to {member.guild.name}", colour=self.bot.colour)
            if member.guild.id == 781796557490094100:
                embed.description = "Hello ! DSCN is an artist collective that also functions as a record label. We believe in giving artists the exposure they require and helping them with forming an audience. We support local growing musicians and help in promoting them. We make no money out of this and we do not do it for profit. We provide distribution for growing artists and production help for beginners.\n"\
                                    "\nCheck out our Server Rules: <#781807335316258856>\n"\
                                    "\nGive yourself some cool roles: <#782673401210601473>"\
                                    "\n[Permanent Discord Invite Link](https://discord.gg/2NVgaEwd2J)"


                embed.set_image(url="https://cdn.discordapp.com/attachments/781811569378066452/785557802865262643/DSCN_Banner.png")
                embed.set_footer(text="DSCN Records")
            elif member.guild.id == 756453096996995075:
                embed.description = "Techspiration is a tech channel on YouTube run by <@488012130423930880> He makes high-quality tech videos and sometimes gaming videos. For him, less is more. That's why he tries to give as much info as he can in the least amount of time. A sub to his channel would be astounding and make sure to follow him on Instagram for crazy BTS."
                value = "This server is not limited to technology only. Take a reaction role such as Tech Enthusiast, Music Producer, Adobe User, Artist, Gamer or a Programmer to unlock specific text channels. We have tried to be inclusive of our community.\n"\
                        "\nCheck out our Server Rules: <#795697454560575508>\n"\
                        "\nGive yourself some cool roles: <#795699507416793099>\n"\
                        "\nAll important links can be found below:\n"\
                        "\n[YouTube Link](https://www.youtube.com/c/Techspiration/featured)\n"\
                        "[Instagram Link](https://www.instagram.com/apratimjain/)\n"\
                        "\n[Permanent Discord Link](https://discord.gg/dP7qdgChJQ)"
                embed.add_field(name="About this server:", value=value, inline=False)
                embed.set_image(url="https://cdn.discordapp.com/attachments/795698922437214241/795716345626361897/banner.png")
                embed.set_footer(text="Techspiration")
                                    
            try:
                await member.send(embed=embed)
            except:
                pass

def setup(bot:commands.Bot):
    bot.add_cog(DiscordEvents(bot))