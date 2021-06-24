from __future__ import annotations

import discord

from discord.ext import commands
from typing import Optional

from utils.bot import Bot
from utils.context import Context

class Administration(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    @commands.has_guild_permissions(manage_guild=True)
    @commands.group(invoke_without_command=True, aliases=['setting'])
    async def settings(self, ctx: Context):
        """Shows settings of your guild for the bot."""
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        prefixes = [self.bot.user.mention]
        prefixes.extend(settings.get('prefixes', ['.']))
        log = settings.get('log', 'None set')
        if isinstance(log, int):
            log = f'<#{log}>'
        
        channel_ids = settings.get('disabledChannels')
        if channel_ids:
            disabledChannels = '\n'.join([f'<#{c}>' for c in channel_ids])
        else:
            disabledChannels = 'None set'
            
        embed = discord.Embed(
            title = 'Guild Settings',
            colour = ctx.bot.colour,
            description = f'**ID:** {ctx.guild.id}',
            timestamp = discord.utils.utcnow()
        )
        
        embed.set_footer(text=ctx.bot.branding)
        
        embed.add_field(
            name = 'Prefixes',
            value = '\n'.join([f'{i}. {p}' for i,p in enumerate(prefixes, 1)])
        )
        
        embed.add_field(
            name = 'Log Channel',
            value = log
        )
        
        embed.add_field(
            name = 'Blacklisted Channels',
            value = disabledChannels
        )
        
        await ctx.send(embed=embed)
        
    @commands.has_guild_permissions(manage_guild=True)
    @settings.group()
    async def prefix(self, ctx: Context):
        """Command group for adding or removing a prefix. """
        if ctx.invoked_subcommand is None:
            return await ctx.send('Use either `prefix add` or `prefix remove` to add or remove a prefix.')
        
    @commands.has_guild_permissions(manage_guild=True)
    @prefix.command(name='add')
    async def addprefix(self, ctx: Context, *, prefix: str):
        """Adds a prefix for the guild. """
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        
        else:
            prefixes = settings.get('prefixes', [])
            prefixes.append(prefix)
            prefixes = list(set(prefixes))
            await self.bot.settings.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'prefixes':prefixes}}
            )
            
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @prefix.command(name='remove')
    async def removeprefix(self, ctx: Context, *, prefix: str):
        """Removes a prefix"""
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')

        else:
            prefixes: list = settings.get('prefixes')
            prefixes.remove(prefix)
            prefixes = list(set(prefixes))
            await self.bot.settings.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'prefixes':prefixes}}
            )
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @settings.command(name='log', aliases=['channel'])
    async def setlog(self, ctx: Context, *, channel: Optional[discord.TextChannel]):
        """Sets or removes a log channel."""
            
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        else:
            await self.bot.settings.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'log':channel.id if channel else None}}
            )
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @settings.command(name='commands', aliases=['command'])
    async def cmds(self, ctx: Context, channel: Optional[discord.TextChannel], *, option: str):
        """Disables or Enables bot commands in a channel.
        
        Enable using: `enable` or `on`
        Disable using: `disable` or `off`
        """
        channel = channel or ctx.channel
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        channels = settings.get('disabledChannels', [])
        if option in ('disable', 'off'):
            channels.append(channel.id)
            update = 'disabled'
        elif option in ('enable', 'on'):
            channels.remove(channel.id)
            update = 'enabled'
        else:
            return await ctx.send('Invalid option given.')
        
        await self.bot.settings.update_one(
            {'guildId':ctx.guild.id},
            {'$set':{'disabledChannels': channels}}
        )
        
        await ctx.tick(True)
        await ctx.send(f'Commands succesfully **{update}** for `#{channel.name}`!')
    @commands.has_guild_permissions(manage_guild=True)
    @commands.command()
    async def setup(self, ctx: Context):
        """Sets up the server so you can enable logging and multiple prefixes."""
        await self.bot.settings.delete_one({'guildId':ctx.guild.id})
           
        document = {
            'guildId':ctx.guild.id,
            'prefixes':['.'],
            'log':None,
            'disabledChannels':[]
        }
        
        await self.bot.settings.insert_one(document)
        
        await ctx.send('Server has been setup successfully!')
        await ctx.tick(True)
    
def setup(bot: Bot):
    bot.add_cog(Administration(bot))