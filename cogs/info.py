from __future__ import annotations
from datetime import datetime

import itertools
import time
import discord
import humanize
import pygit2
import pkg_resources
import psutil

from discord.ext import commands
from utils.bot import Bot
from utils.context import Context
from utils.checks import botchannel
from utils.utils import DSCN_GUILD, Embed, human_time
from typing import Union, Optional

class Info(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.process = psutil.Process()

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
            embed.add_field(name='Nickname', value=user.nick or 'None set')
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
                value = ', '.join(f"{f}".replace('_', ' ').title() for f in guild.features),
                inline = False
            )
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            
        await ctx.send(embed=embed)
    
    def format_commit(self, commit):
        short, _, _ = commit.message.partition('\n')
        short_sha2 = commit.hex[0:6]
        
        # [`hash`](url) message
        return f'[`{short_sha2}`](https://github.com/Rapptz/RoboDanny/commit/{commit.hex}) {short}'

    def get_last_commits(self, count=3):
        repo = pygit2.Repository('.git')
        commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return '\n'.join(self.format_commit(c) for c in commits)
    
    @botchannel()
    @commands.command()
    async def about(self, ctx: Context):
        """Gives info on the bot."""
        revision = self.get_last_commits()
        
        embed = discord.Embed(
            title = 'Official Bot Server Invite',
            url = 'https://discord.gg/2NVgaEwd2J',
            colour = self.bot.colour,
            description = 'Latest Changes:\n'+revision
        )
        
        guild: discord.Guild = self.bot.get_guild(DSCN_GUILD)
        owner = guild.get_member(self.bot.owner_id)
        if not owner:
            owner = await guild.fetch_member(self.bot.owner_id)
            
        embed.set_author(name=str(owner), icon_url=owner.avatar.url)
        
        total_members = 0
        total_unique = len(self.bot.users)
        
        text = 0
        voice = 0
        guilds = 0
        
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable:
                continue
            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1
                    
        embed.add_field(name='Members', value=f'{total_members} total\n{total_unique} unique')
        embed.add_field(name='Channels', value=f'{text + voice} total\n<:text:824903975626997771>{text} <:voice:824903975098777601>{voice}')
        
        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU')

        version = pkg_resources.get_distribution('discord.py').version
        embed.add_field(name='Guilds', value=guilds)
        embed.add_field(name='Commands', value=len(self.bot.commands))
        embed.add_field(name='Uptime', value=humanize.naturaltime(self.bot.uptime, when=datetime.utcnow()))
        embed.set_footer(text=f'Made with discord.py v{version}', icon_url='http://i.imgur.com/5BFecvA.png')
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)
        
        
    @botchannel()
    @commands.command()
    async def ping(self, ctx: Context):
        """Shows the bot's ping."""
        
        start = time.perf_counter()
        msg = await ctx.send('Pinging...')
        end = time.perf_counter()
        
        typing_latency = (end-start)*1000
        websocket_latency = self.bot.latency*1000
        
        start = time.perf_counter()
        await self.bot.settings.find_one({'guildId':ctx.guild.id})
        end = time.perf_counter()
        
        mongo_latency = (end-start)*1000
        
        embed = Embed(title='\U0001f3d3 Pong!')
        embed.add_field(
            name = '<a:typing:828718094959640616> | Typing',
            value = f'`{typing_latency:.2f}ms`'
        )
        embed.add_field(
            name = '<a:settings:801424449542815744> | Websocket',
            value = f'`{websocket_latency:.2f}ms`'
        )
        embed.add_field(
            name = '<:mongo:814706574928379914> | Database',
            value = f'`{mongo_latency:.2f}ms`'
        )
        
        await msg.edit(content=None, embed=embed)
        
    @botchannel()
    @commands.command()
    async def prefix(self, ctx: Context):
        """Shows all the set prefix for the guild."""
        base = [self.bot.user.mention]
        settings = await self.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings:
            base.extend(settings['prefixes'])
        else:
            base.append('.')
            
        embed = Embed(
            title=f'Prefixes for {ctx.guild.name}',
            description='\n'.join(f'{i}. {p}' for i,p in enumerate(base, 1)),
            footer=f'ID: {ctx.guild.id}'
        )
        
        await embed.send(ctx.channel)
        
    @botchannel()
    @commands.command(aliases=['av'])
    async def avatar(self, ctx: Context, *, user: Optional[discord.User]):
        """Shows avatar of a user."""
        user = user or ctx.author
        
        def url_as(format: str) -> str:
            return user.avatar.with_format(format).url
        
        embed = Embed(
            title = f'Avatar for {user}',
            description=(
                f'Link As\n'\
                f'[png]({url_as("png")}) | [jpg]({url_as("jpg")}) | [webp]({url_as("webp")})'
            )
        )
        
        embed.set_image(url=user.avatar.url)
        await embed.send(ctx.channel)
        
    @botchannel()
    @commands.command()
    async def invite(self, ctx: Context):
        """Gives an invite for the bot"""
        
        def get_link(permissions: discord.Permissions) -> str:
            return discord.utils.oauth_url(self.bot.user.id, permissions)
        
        embed = Embed(
            title = 'Invite Links',
            description = (
                f'[Invite Link (Minimal Perms)]({get_link(discord.Permissions(2147863616))})\n'\
                f'[Invite Link (Admin)]({get_link(discord.Permissions(8))})\n'\
                f'[Bot Server](https://discord.gg/2NVgaEwd2J)'
            )
        )
        
        await embed.send(ctx.channel)
        
def setup(bot: Bot):
    bot.add_cog(Info(bot))