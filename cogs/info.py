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

import discord, json, asyncio, psutil, platform, multiprocessing, time

import inspect
import os

from discord.ext import commands
from utils.checks import bot_channel, is_staff
from utils.requests import Requests
from utils.db import DatabaseConnection
from datetime import datetime
from typing import Counter, Optional

from jishaku import Jishaku


with open("utils/vars.json") as f:
    data = json.load(f)

version = data['version']
footer = data['footer']
colour = int(data['colour'],16)
LogChannel = data['channels']['LogChannel']


class Information(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.requests = Requests()
        self.artistDb = DatabaseConnection("Info")
        self.LogChannel = self.bot.get_channel(LogChannel)
        if self.LogChannel is None:
            self.LogChannel = self.bot.get_channel(789191146647322624)

    @commands.guild_only()
    @bot_channel()
    @commands.command(name="userinfo", aliases=["ui", "whois", "user"])
    async def userInfo(self, ctx:commands.Context, member:discord.Member = None):
        """
        Shows some useful info about the given user.
        """
        if member is None: member = ctx.author

        status = {
            "online":"<:online:789399319727046696> `Online`",
            "offline":"<:offline:789399319915790346> `Offline`",
            "dnd":"<:dnd:789399319400153098> `Do Not Disturb`",
            "idle":"<:idle:789399320029560852> `Idle`"
        }

        embed = discord.Embed(title=member.name, colour=member.colour)
        embed.add_field(name="General Info", 
                        value=f"Name: `{member}`\n"
                              f"Status: {status[str(member.status)]}\n"
                              f"Created at: `{datetime.strftime(member.created_at, '%a %d, %B of %Y at %H:%M%p')}`",
                        inline=False)

        embed.add_field(name="Server Related",
                        value=f"Joined us at: `{datetime.strftime(member.joined_at, '%a %d, %B of %Y at %H:%M%p')}`\n"
                              f"Roles: {' '.join([r.mention for r in member.roles if r != ctx.guild.default_role] or ['None'])}",
                        inline=False)

        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=f"Member Id: {member.id} | {footer}")

        await ctx.send(embed=embed)


    @commands.guild_only()
    @bot_channel()
    @commands.command(name="serverinfo", aliases=["si","server", "guild", "guildinfo"])
    async def serverInfo(self, ctx:commands.Context):
        """
        Shows some useful information about the server
        """
        thing = f"**Owners:** <@449897807936225290>, <@393378646162800640>, <@488012130423930880>\n**Created on:** {datetime.strftime(ctx.guild.created_at, '%a %d, %B of %Y at %H:%M%p')}"
        embed = discord.Embed(title=ctx.guild.name, colour=colour)
        embed.description = ctx.guild.description+thing if ctx.guild.description else thing
        embed.add_field(name="Region", value=f"{ctx.guild.region}".upper(), inline=False)

        info = []
        features = set(ctx.guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner'
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'<:tick:789438127738978304>: {label}')

        if info:
            embed.add_field(name='Features', value='\n'.join(info))

        embed.add_field(name=f"Channels ({len(ctx.guild.text_channels)+len(ctx.guild.voice_channels)})",
                        value=f"<:text:789428500003029013> Text: {len(ctx.guild.text_channels)}\n<:voice:789428500309475408> Voice: {len(ctx.guild.voice_channels)}",
                        inline=False)

        bots = len([m for m in ctx.guild.members if m.bot])
        humans = ctx.guild.member_count - bots

        embed.add_field(name=f"Members ({ctx.guild.member_count})",
                        value=f"<:member:789445545915580486> Humans: {humans}\n\\🤖 Bots: {bots}")
        

        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_image(url=ctx.guild.banner_url)
        embed.set_footer(text=f"Guild Id: {ctx.guild.id} | {footer}")
        await ctx.send(embed=embed)

    @bot_channel()
    @commands.command(name="avatar", aliases=["av"])
    async def userAvatar(self, ctx:commands.Context, member:discord.Member=None):
        """
        Gets the avatar of the member given
        """
        if member is None: member=ctx.author
        embed = discord.Embed(colour=colour)
        embed.set_author(name=member)
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @bot_channel()
    @commands.command(name="permissions", aliases=["serverperms", "perms", "guildperms", "guildpermissions"])
    async def memberGuildPerms(self, ctx:commands.Context, member:discord.Member=None):
        """
        Shows the permssions the given member has
        """
        if member is None: member = ctx.author

        perms = "\n".join(p for p, value in member.guild_permissions if value)

        embed=discord.Embed(title="Server Permissions",colour=colour)
        embed.description = f"{member} has the following permissions:\n```yaml\n{perms}```"
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)

          
    @bot_channel()
    @commands.command()
    async def ping(self, ctx:commands.Context):
        """Shows the bot ping"""
        start = time.perf_counter()
        msg:discord.Message = await ctx.send("Pinging...")
        end = time.perf_counter()
        duration = (end-start)*1000
        db_start = time.perf_counter()
        c = await self.artistDb.count
        db_end = time.perf_counter()
        db_duration = (db_end - db_start)*1000
        emb = discord.Embed(colour=self.bot.colour)
        emb.add_field(name="<a:typing:800335819764269096> | Typing", value=f"`{duration:.2f}ms`")
        emb.add_field(name="<:DSCN:785553966389788682> | Websocket", value=f"`{round(self.bot.latency*1000)}ms`")
        emb.add_field(name="<:mongodb:800335852693094510> | Database", value=f"`{db_duration:.2f}ms`")

        await msg.edit(content=None,embed=emb)
        

    @bot_channel()
    @commands.command(name="credits",aliases=['credit'])
    async def creds(self, ctx:commands.Context):
        """See the credits for the bot"""
        embed = discord.Embed(title="Credits", colour=colour)
        
        main_dev = "<@!449897807936225290> ([ItsArtemiz#8858](https://discord.com/users/449897807936225290)) - Main Developer"
        art = "<@!393378646162800640> ([brryalln#6446](https://discord.com/users/393378646162800640)) - Bot Art"
        opt_adv = "<@!488012130423930880> ([appyeet#4034](https://discord.com/users/488012130423930880)) - Optimizations and Advice"

        embed.description = main_dev+"\n"+art+"\n"+opt_adv

        embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @bot_channel()
    @commands.command(aliases=['botstats'])
    async def stats(self, ctx:commands.Context):
        """Shows stats about the bot"""
        embed = discord.Embed(title="<a:loading:801422257221271592> Gathering Stats", colour=self.bot.colour)
        msg = await ctx.send(embed=embed)
        channel_types = Counter(type(c) for c in self.bot.get_all_channels())
        voice = channel_types[discord.channel.VoiceChannel]
        text = channel_types[discord.channel.TextChannel]
        infoembed = discord.Embed(
            title="<a:settings:801424449542815744> Stats",
            description=f"<:member:789445545915580486> Member Count: `{len(self.bot.users)}`\n<:discord:801425079937663017> Servers: `{len(self.bot.guilds)}`\n<:code:801425080936038400> Commands: `{len(self.bot.commands)}`\n<:text:789428500003029013> Text Channels: `{text}`\n<:voice:789428500309475408> Voice Channels: `{voice}`\n<:dpy:789493535501058078> DPY Version: `{discord.__version__}`\n<:python:789493535493718026> Python Version: `{platform.python_version()}`\n<:server:801426535637712956> Server: `{platform.system()}`\n> CPU Count: `{multiprocessing.cpu_count()}`\n> CPU Usage: `{psutil.cpu_percent()}%`\n> RAM: `{psutil.virtual_memory().percent}%`",
            colour=self.bot.colour
        )
        infoembed.set_footer(text=f"Version {version}")
        await asyncio.sleep(2)
        await msg.edit(embed=infoembed)


    @bot_channel()
    @commands.command(aliases=['ut'])
    async def uptime(self, ctx:commands.Context):
        """Shows bot uptime"""
        delta_uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"I have been awake for: **{days}d, {hours}h, {minutes}m, {seconds}s**")
    
    @bot_channel()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.group(aliases=['artists'],invoke_without_command=True)
    async def artist(self, ctx:commands.Context, *,name:str=None):
        """Shows the registered artists"""
        if name is None:
            embed = discord.Embed(
                title="All Verified DSCN Artists",
                colour=self.bot.colour,
                timestamp=datetime.utcnow()
            )
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text=footer)
            description = ""
            artists = await self.artistDb.fetch_all
            async for a in artists:
                description+=f"• `{a['name']}` - {a['type']} | [Latest Release]({a['latest']})\n"
            embed.description = description
            return await ctx.send(embed=embed)
        
        a = await self.artistDb.fetch({'name':name})
        embed = discord.Embed(
            title=f"Artist: `{name}`",
            colour=self.bot.colour,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=footer)
        embed.add_field(name="Music Style", value=a['type'])
        embed.add_field(name="Latest Release", value=a['latest'], inline=False)
        return await ctx.send(embed=embed)

    @artist.command(name="add", aliases=['a'])
    @commands.is_owner()
    async def _add(self, ctx:commands.Context, name:str, type:str, latest:str=None):
        """Adds the artist into the database.
        If the artist already has a track released, you can mention it at the last"""
        artists = await self.artistDb.fetch_all
        async for a in artists:
            if a['name'] == name:
                return await ctx.send(f"Artist {a['name']} is already in the system with music style {a['type']}.")

        post = {
            'name':name,
            'type':type.capitalize(),
            'latest':latest or "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }

        insert = await self.artistDb.insert(post)
        if insert:
            return await ctx.send(
                f"Added artist `{name}` with music style: {type}."
            )
        else:
            return await ctx.send("An error occured")

    @artist.command(aliases=['m'])
    @commands.is_owner()
    async def modify(self, ctx:commands.Context, field:str, name:str, value:str):
        """Modifies an existing value for a given artist"""
        if field not in ('name','latest','type'):
            return await ctx.send("Invalid field given. Valid fields are: `name`, `latest` ,`type`")
        old = await self.artistDb.fetch({'name':name})
        if not old:
            return await ctx.send(f"There is no such artist by the name `{name}` registered.")

        update = await self.artistDb.update({'name':name}, {f'{field}':value})
        if update:
            return await ctx.send(f"Changed {old[f'{field}']} → {value}")
        else:
            return await ctx.send("Couldn't update..")

    @artist.command(aliases=['d'])
    @commands.is_owner()
    async def delete(self, ctx:commands.Context, *,name:str):
        """Deletes a record from the database"""
        a = await self.artistDb.fetch({'name':name})
        if not a:
            return await ctx.send(f"There is no such artist by the name `{name}` registered.")
        embed = discord.Embed(
            title=f"Artist: `{name}`",
            colour=self.bot.colour,
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=footer)
        embed.add_field(name="Music Style", value=a['type'])
        embed.add_field(name="Latest Release", value=a['latest'], inline=False)

        await ctx.send("Are you sure you want to delete the following data:", embed=embed)

        def check(m:discord.Message):
            return m.channel == ctx.channel and m.author == ctx.author
        try:
            message:discord.Message = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout reached. Cancelling command")
        else:
            if message.content.lower() in ('y', 'yes'):
                await self.artistDb.delete_one({'name':name})
                await ctx.send("\U0001f44c Done")
            else:
                await ctx.send("Invalid option given. Valid options are 'y' or 'yes'")


    @commands.command(aliases=['src'])
    @bot_channel()
    async def source(self, ctx:commands.Context,*,command:str=None):
        """Shows source of the bot or a command"""
        if not command:
            embed = discord.Embed(title="Bot's Source Code",
                                  description="The source is distributed under [GPL-3.0 License](https://github.com/Team-DSCN/DSCN-Bot/blob/main/LICENSE)\nDon't forget to leave a star ⭐",
                                  url=ctx.bot.github_url, colour=ctx.bot.colour)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text=footer)
            return await ctx.send(embed=embed)

        command = ctx.bot.help_command if command.lower() == "help" else ctx.bot.get_command(command)
        if not command:
            return await ctx.send("Couldn't find command.")
        if isinstance(command.cog, Jishaku):
            return await ctx.send("<https://github.com/Gorialis/jishaku>")

        if isinstance(command, commands.HelpCommand):
            lines, starting_line_num = inspect.getsourcelines(type(command))
            filepath = f"{command.__module__.replace('.', '/')}.py"
        else:
            lines, starting_line_num = inspect.getsourcelines(command.callback.__code__)
            filepath = f"{command.callback.__module__.replace('.', '/')}.py"

        ending_line_num = starting_line_num + len(lines) - 1
        command = "help" if isinstance(command, commands.HelpCommand) else command
        embed = discord.Embed(
            title=f"Source on command: `{command}`",
            description="The source is distributed under [GPL-3.0 License](https://github.com/Team-DSCN/DSCN-Bot/blob/main/LICENSE)\nDon't forget to leave a star ⭐",
            url=f"{self.bot.github_url}/blob/master/{filepath}#L{starting_line_num}-L{ending_line_num}",
            colour=ctx.bot.colour)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=footer)
        await ctx.send(embed=embed)


            

def setup(bot:commands.Bot):
    bot.add_cog(Information(bot))