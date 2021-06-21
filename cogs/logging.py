from __future__ import annotations
from typing import Optional
from utils.bot import Bot
from utils.utils import log, Embed
import discord

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
        
def setup(bot: Bot):
    bot.add_cog(EventLogger(bot))