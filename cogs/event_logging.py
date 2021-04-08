# -*- codingL utf-8 -*-

"""
Event Logging Module
~~~~~~~~~~~~~~~~~~~~

This file logs various events.

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
import humanize

from typing import Union
from datetime import datetime
from discord.ext import commands

from utils.channel_logging import post_log, embed_builder

class EventLogging(commands.Cog):
    """
    A logging module. That's all.
    """
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    async def update_member_nick(self, member:discord.Member) -> None:
        """Updates a user's nickname if it is not typeable on a standard English QWERTY keyboard.

        Parameters
        ----------
        member : Member
            The discord member to update.

        Returns
        -------
        None
        """
        string = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[]^_`{|}~"""

        for l in member.name:
            if l in string:
                return
        else:
            try:
                await member.edit(nick=f"Mod Nick {member.id}")
            except discord.HTTPException:
                await member.edit(nick=f"Nick {member.id}")
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message_delete(self, message:discord.Message):
        # This event is triggered when a message is deleted.
        # This message should be in the bot's cache.

        if message.author.bot:
            return # We don't want to log a bot's messages.

        embed = embed_builder(
            bot=self.bot,
            title = f"Message Deleted in #{message.channel}",
            user = message.author,
            colour = discord.Color.red(),
            description=message.content,
            footer="Deleted At"
        )

        await post_log(message.guild, name="bot-logs", embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before:discord.Message, after:discord.Message):
        # This event is triggered when a message is edited.
        # This message should be in the bot's cache.

        if before.author.bot:
            return # We don't want to log a message edited by a bot.

        sign = "+"
        if len(after.content) > len(before.content):
            sign = "+"
        elif len(after.content) < len(before.content):
            sign = "-"
        else:
            sign = ""


        embed = embed_builder(
            bot=self.bot,
            title = f"Message Edited in #{after.channel}",
            footer = "Edited At",
            description = f"[Jump to Message]({after.jump_url})\n**Before:** {before.content}\n**{sign}After:** {after.content}",
            user = after.author
        )
    
        await post_log(after.guild, name="bot-logs", embed=embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages:list):
        # This event gets triggered when messages are deleted in bulk.
        # The messages need to be in bot's cache.
        deleted = []
        shown = []
        description = ""
        sample = None
        for msg in messages:
            deleted.append(msg)
            if len(msg.content) > 100:
                pass
            if len(description + msg.content) > 2000:
                pass
            else:
                description += f"**[{msg.author}]:** {msg.content}\n"
                shown.append(msg)
            sample:discord.Message = msg
        embed = discord.Embed(
            title = f"{len(messages)} Messages deleted in #{sample.channel.name}",
            timestamp = datetime.utcnow(),
            description = description,
            colour = discord.Color.red()
        )
        embed.set_footer(text=f"{len(shown)} messages shown")

        await post_log(sample.guild, name="bot-logs", embed=embed)


    @commands.Cog.listener()
    async def on_member_join(self, member:discord.Member):
        # This event is triggered when a user joins the guild.
        
        description = f"{member.mention} {humanize.intcomma(humanize.ordinal(len(member.guild.members)))} to join. \n created {humanize.precisedelta(member.created_at - datetime.utcnow(), format='%0.0f', minimum_unit='minutes')} ago"

        embed = embed_builder(
            bot=self.bot,
            title = "Member Joined",
            description=description,
            colour=discord.Color.green(),
            user = member,
            footer="Joined At"
        )

        await post_log(member.guild, name="bot-logs", embed=embed)
        await self.update_member_nick(member)

    @commands.Cog.listener()
    async def on_member_remove(self, member:discord.Member):
        # This event gets triggered when a member leaves/ gets kicked from the guild.

        description = f"{member.mention} joined {humanize.precisedelta(member.joined_at - datetime.utcnow(), format='%0.0f')} ago"
        embed = embed_builder(
            bot=self.bot,
            title="Member Left",
            description=description,
            user = member,
            footer = f"ID: {member.id}",
            colour = discord.Colour.from_rgb(255, 46, 41)
        )

        roles = member.roles
        roles.remove(member.guild.default_role)
        if roles:
            embed.add_field(
                name="Roles",
                value=",".join([r.mention for r in roles])
            )

        await post_log(member.guild, name="bot-logs", embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild:discord.Guild, user:Union[discord.User, discord.Member]):
        # This event is called when a user is banned from the guild.

        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
            entry: discord.AuditLogEntry = entry
            if entry.target.id == user.id:
                reason = f"**Reason:** {entry.reason if entry.reason else 'No reason was provided.'} \n **Moderator:** {entry.user.mention} (ID: `{entry.user.id}`)"
                break

        embed = embed_builder(
            bot=self.bot,
            title = "Member Banned",
            description=reason,
            user=user,
            colour = discord.Colour.dark_red()
        )
            
        await post_log(guild=guild, name="bot-logs", embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild:discord, user:discord.User):
        # This event is called when a user is unbanned from the guild.

        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
            entry: discord.AuditLogEntry = entry
            if entry.target.id == user.id:
                reason = f"**Reason: ** {entry.reason if entry.reason else 'No reason provided.'} \n **Moderator: ** {entry.user.mention} (ID: `{entry.user.id}`)"
                break

        embed = embed_builder(
            bot=self.bot,
            title = "Member Unbanned",
            description=reason,
            user=user,
            colour = discord.Color.from_rgb(100, 255, 70)
        )

        await post_log(guild=guild, name="bot-logs", embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before:discord.Member, after:discord.Member):
        # This event is called when a member is updated. Check discord.py docs for all the events.

        if before.bot:
            return
        
        if before.nick != after.nick:
            await self.update_member_nick(after)
            embed = embed_builder(
                bot = self.bot,
                title = "Nickname Update",
                description=f"**Before:** {before.nick if before.nick else before.display_name}\n**After:** {after.nick if after.nick else after.display_name}",
                user = before,
                colour=discord.Color.blue(),
                footer="Updated At"
            )

            await post_log(guild=before.guild, name="bot-logs", embed=embed)

        if before.roles != after.roles:
            embed = embed_builder(
                bot=self.bot,
                title="Roles Updated",
                description="",
                user=before,
                colour=discord.Color.blue(),
                footer="Updated At"
            )

            temp = list(set(before.roles + after.roles))
            added = []
            removed = []
            for role in temp:
                if role in before.roles and role not in after.roles:
                    removed.append(role)
                elif role in after.roles and role not in before.roles:
                    added.append(role)
            
            if added:
                embed.add_field(name="Roles Added", value=", ".join([r.mention for r in added]), inline=False)
            if removed:
                embed.add_field(name="Roles Removed", value=", ".join([r.mention for r in removed]), inline=False)

            await post_log(guild=before.guild, name="bot-logs", embed=embed)

def setup(bot:commands.Bot):
    bot.add_cog(EventLogging(bot))