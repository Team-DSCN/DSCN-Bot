from __future__ import annotations

import discord

from discord.ext import commands
from utils.bot import Bot
from utils.context import Context
from utils.checks import botchannel
from utils.utils import DSCN_GUILD, human_time
from typing import Union, Optional

class Info(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @botchannel()
    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx: Context, *, user: Optional[Union[discord.Member, discord.User]]):
        """ Gets info on a user. """
        user = user or ctx.author
        embed = discord.Embed(
            title = 'User Information',
            timestamp = discord.utils.utcnow()
        )
        embed.add_field(name='Name', value=str(user))
        embed.add_field(name='ID', value=f'`{user.id}`')
        embed.set_thumbnail(url=user.avatar.url)
        if isinstance(user, discord.Member):
            embed.colour = ctx.bot.colour
            embed.add_field(name='Nickname', value=user.nick)
            embed.add_field(name='Created At', value=human_time(user.created_at, minimum_unit='minutes'), inline=False)
            embed.add_field(name='Joined At', value=human_time(user.joined_at, minimum_unit='minutes'), inline=False)
            members: list = ctx.guild.members
            members.sort(key=lambda m: m.joined_at)
            embed.add_field(name='Join Position', value=members.index(user) + 1, inline=False)

            roles = user.roles
            roles.remove(ctx.guild.default_role)
            if roles:
                embed.add_field(
                    name = 'Roles',
                    value = ', '.join([r.mention for r in roles]) if len(roles) <= 7 else f'{len(roles)} roles',
                    inline = False
                )
        else:
            embed.set_author(name='This user is not in the server')

        await ctx.send(embed=embed)

    @botchannel()
    @commands.guild_only()
    @commands.command(aliases=['si'])
    async def serverinfo(self, ctx: Context):
        """Shows the server's info."""
        guild: discord.Guild = ctx.guild
        
        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)
                
        description = f'**ID:** {guild.id}'
        if guild.id != DSCN_GUILD:
            description += f' | **Owner:** {guild.owner}'
        embed = discord.Embed(
            title = str(guild),
            description = description,
            colour = ctx.bot.colour,
            timestamp = guild.created_at
        )
        
        embed.set_footer(text='Created')
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        key_to_emoji = {
            "text":"<:text:824903975626997771>",
            "voice":"<:voice:824903975098777601>"
        }
        
        text = len(guild.text_channels)
        voice = len(guild.voice_channels)
        
        embed.add_field(name='Members', value=guild.member_count)
        embed.add_field(name='Voice Region', value=str(guild.region).title())
        embed.add_field(
            name = 'Channels',
            value = f'{key_to_emoji["text"]} {text} {key_to_emoji["voice"]} {voice}'
        )
        embed.add_field(name='Roles', value=f'{len(guild.roles)} roles')
        s = 0
        a = 0
        for e in guild.emojis:
            if e.animated:
                a+=1
            else:
                s+=1
                
        embed.add_field(
            name = f'Emojis ({len(guild.emojis)})',
            value = f'Static: {s}\n'\
                    f'Animated: {a}'
        )
        
        embed.add_field(
            name = 'Boosts',
            value = f'{guild.premium_subscription_count} boosts (Level {guild.premium_tier})'
        )
        if guild.features:
            embed.add_field(
                name = 'Features',
                value = ', '.join(f"{f}".replace('_', ' ').capitalize() for f in guild.features),
                inline = False
            )
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            
        await ctx.send(embed=embed)
    
    @commands.has_guild_permissions(manage_guild=True)
    @commands.group(invoke_without_command=True)
    async def settings(self, ctx: Context):
        """Shows settings of your guild for the bot."""
        settings = await self.bot.utils.find_one({'guildId':ctx.guild.id})
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
        settings = await self.bot.utils.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        
        else:
            prefixes = settings.get('prefixes', [])
            prefixes.append(prefix)
            prefixes = list(set(prefixes))
            await self.bot.utils.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'prefixes':prefixes}}
            )
            
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @prefix.command(name='remove')
    async def removeprefix(self, ctx: Context, *, prefix: str):
        """Removes a prefix"""
        settings = await self.bot.utils.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')

        else:
            prefixes: list = settings.get('prefixes')
            prefixes.remove(prefix)
            prefixes = list(set(prefixes))
            await self.bot.utils.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'prefixes':prefixes}}
            )
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @settings.command(name='log', aliases=['channel'])
    async def setlog(self, ctx: Context, *, channel: Optional[discord.TextChannel]):
        """Sets or removes a log channel."""
            
        settings = await self.bot.utils.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return await ctx.send(f'Please run `{ctx.clean_prefix}setup` first.')
        else:
            await self.bot.utils.update_one(
                {'guildId':ctx.guild.id},
                {'$set':{'log':channel.id if channel else None}}
            )
        await ctx.tick(True)
        
    @commands.has_guild_permissions(manage_guild=True)
    @settings.command(name='commands')
    async def cmds(self, ctx: Context, channel: Optional[discord.TextChannel], *, option: str):
        """Disables or Enables bot commands in a channel.
        
        Enable using: `enable` or `on`
        Disable using: `disable` or `off`
        """
        channel = channel or ctx.channel
        settings = await self.bot.utils.find_one({'guildId':ctx.guild.id})
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
        
        await self.bot.utils.update_one(
            {'guildId':ctx.guild.id},
            {'$set':{'disabledChannels': channels}}
        )
        
        await ctx.tick(True)
        await ctx.send(f'Commands succesfully **{update}** for the current channel!')
    @commands.has_guild_permissions(manage_guild=True)
    @commands.command()
    async def setup(self, ctx: Context):
        """Sets up the server so you can enable logging and multiple prefixes."""
        await self.bot.utils.delete_one({'guildId':ctx.guild.id})
           
        document = {
            'guildId':ctx.guild.id,
            'prefixes':['.'],
            'log':None,
            'disabledChannels':[]
        }
        
        await self.bot.utils.insert_one(document)
        
        await ctx.send('Server has been setup successfully!')
        await ctx.tick(True)
def setup(bot: Bot):
    bot.add_cog(Info(bot))