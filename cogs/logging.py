from __future__ import annotations
import discord
import humanize

from typing import Optional
from utils.bot import Bot
from utils.utils import human_time, Embed

from discord.ext import commands


class EventLogger(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def check_log_channel(self, guild: discord.Guild) -> Optional[discord.TextChannel]:
        """Checks if a log channel is set for the current guild or not.

        Parameters
        ----------
        guild : discord.Guild
            The guild to search the channel in.

        Returns
        -------
        Optional[discord.TextChannel]
            The channel if set or None.
        """
        settings = await self.bot.utils.find_one({'guildId':guild.id})
        if not settings:
            return
        
        channel_id = settings.get('log')
        if channel_id:
            channel = guild.get_channel(channel_id)
            if not channel:
                channel = await guild.fetch_channel(channel_id)
                
            if isinstance(channel, discord.TextChannel):
                return channel
            else:
                return
        else:
            return
    
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        channel = await self.check_log_channel(message.guild)
        if channel is None:
            return
        
        embed = Embed(
            author = message.author,
            colour = discord.Colour.red(),
            footer = 'Deleted At',
            title = 'Message Deleted',
            description = f'**Channel:** {message.channel.mention}'
        )
        
        if message.content:
            embed.add_field(
                name = 'Content',
                value = message.content,
                inline = False
            )
            
        if message.attachments:
            embed.add_field(
                name='Attachments',
                value=', '.join(f'{a.filename} ({a.content_type})' for a in message.attachments)
            )
            
        await embed.send(channel)
        
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        
        
        deleted = [m for m in messages if len(m.content) <= 200]
        description = '\n'.join(f'**[{m.author}]:** {m.content}' for m in deleted)
        dummy = messages[0]
        
        channel = await self.check_log_channel(dummy.guild)
        if not channel:
            return
        
        if len(description) > 2048:
            description = f'Too many messages to show. {len(messages)} messages were deleted'
        
        embed = Embed(
            colour = discord.Colour.red(),
            title = f'{len(messages)} messages deleted in #{dummy.channel}',
            description = description,
            footer = f'{len(deleted)} messages are shown.'
        )
        
        await embed.send(channel)
        
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
        if before.author.bot:
            return
        channel = await self.check_log_channel(before.guild)
        if not channel:
            return
        
        if before.content != after.content:
            embed = Embed(
                author = before.author,
                colour = discord.Colour.blue(),
                footer = 'Modified At',
                title = 'Message Edited',
                description = f'**Channel:** {before.channel.mention}'
            )
            
            embed.add_field(name='Before', value=before.content, inline=False)
            embed.add_field(name='After', value=after.content, inline=False)
            
            await embed.send(channel)
            
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = await self.check_log_channel(member.guild)
        if not channel:
            return
        
        new = ''
        if member.created_at.day < 3:
            new = '\N{WARNING SIGN} **New Member:** '
        
        embed = Embed(
            colour = discord.Colour.green(),
            footer = 'Joined At',
            author = member,
            title = 'Member Joined',
            description = (
                f'{member.mention} {humanize.intcomma(humanize.ordinal(len(member.guild.members)))} to join.\n'\
                f'{new}created {human_time(member.created_at - discord.utils.utcnow(), minimum_unit="minutes")}.'
            )
        )
        
        await embed.send(channel)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = await self.check_log_channel(member.guild)
        if not channel:
            return
        
        members: list[discord.Member] = member.guild.members
        members.sort(key=lambda m: m.joined_at)
        
        index = members.index(member)
        
        embed = Embed(
            author = member,
            colour = discord.Colour.red(),
            footer = f'ID: {member.id}',
            description = (
                f'{member.mention} joined {human_time(member.joined_at - discord.utils.utcnow())}.\n'\
                f'{humanize.ordinal(index)} to join.'
            )
        )
        
        roles = member.roles
        roles.remove(member.guild.default_role)
        
        if roles:
            embed.add_field(name='Roles', value=', '.join(r.mention for r in roles))
            
        await embed.send(channel)
        
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.bot:
            return
        
        channel = await self.check_log_channel(before.guild)
        if not channel:
            return
        
        if before.display_name != after.display_name:
            embed = Embed(
                author = after,
                colour = discord.Colour.blue(),
                footer = 'Modified At',
                title = 'Nickname Updated',
                description = (
                    f'**Before:** {before.display_name}\n'\
                    f'**After:** {after.display_name}'
                )
            )
            
            await embed.send(channel)
            
        if before.roles != after.roles:
            embed = Embed(
                title = 'Roles Updated',
                colour = discord.Colour.blue(),
                author = after,
                footer = 'Modified At'
            )
            
            temp: list[discord.Role] = list(set(before.roles + after.roles))
            added = []
            removed = []
            
            for role in temp:
                if role in before.roles and role not in after.roles:
                    removed.append(role)
                elif role in after.roles and role not in before.roles:
                    added.append(role)
                    
            if added:
                embed.add_field(
                    name = 'Roles Added',
                    value = ', '.join([r.mention for r in added]),
                    inline = False
                )
            
            if removed:
                embed.add_field(
                    name = 'Roles Added',
                    value = ', '.join([r.mention for r in removed]),
                    inline = False
                )
                
            await embed.send(channel)
            
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.Member | discord.User):
        if not guild.me.guild_permissions.view_audit_log:
            return
        
        channel = await self.check_log_channel(guild)
        if not channel:
            return
        
        async for entry in guild.audit_logs(action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                reason = (
                    f'**Reason:** {entry.reason if entry.reason else "No reason was provided."}\n'\
                    f'**Moderator:** {entry.user.mention} (ID: `{entry.user.id}`)'
                )
                break
            
        embed = Embed(
            title = 'Member Banned',
            description = reason,
            colour = discord.Colour.dark_red(),
            author = user
        )
            
        await embed.send(channel)
        
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        if not guild.me.guild_permissions.view_audit_log:
            return
        
        channel = await self.check_log_channel(guild)
        if not channel:
            return
        
        async for entry in guild.audit_logs(action=discord.AuditLogAction.unban):
            if entry.target.id == user.id:
                reason = (
                    f'**Reason:** {entry.reason if entry.reason else "No reason was provided."}\n'\
                    f'**Moderator:** {entry.user.mention} (ID: `{entry.user.id}`)'
                )
                break
            
        embed = Embed(
            title = 'Member Unbanned',
            description = reason,
            colour = discord.Colour.green(),
            author = user
        )
            
        await embed.send(channel)
        
def setup(bot: Bot):
    bot.add_cog(EventLogger(bot))