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

import discord, json, asyncio, psutil, platform

import inspect
import os

from discord.ext import commands
from utils.utils import Checks, Requests
from utils.db import DatabaseConnection
from datetime import datetime
from typing import Optional

botcmdchannel = Checks().botcmdchannel
botorowner = Checks().botorowner


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
    @botorowner()
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
    @botorowner()
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

    @botorowner()
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

    @botorowner()
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

    @botorowner()
    @commands.command(name="source", aliases=["src"])
    async def source_command(self, ctx:commands.Context,):
        """
        Displays the full source code or for a specific command.
        """
        url = "https://github.com/Team-DSCN/DSCN-Bot"

        embed = discord.Embed(title="Source",timestamp=datetime.utcnow(), colour=colour)
        embed.description = f"{self.bot.user.name}'s code can be found [here]({url}).\nIt is available under the [GPLv3 License](https://github.com/Team-DSCN/DSCN-Bot/blob/main/LICENSE)."
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_footer(text=footer)
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

       
    @botorowner()
    @commands.command()
    async def ping(self, ctx:commands.Context):
        """Shows the bot ping"""
        m1:discord.Message = await ctx.send("Pinging...")
        await asyncio.sleep(0.5)
        await m1.edit(content=f"Pong! Average Latency is {round(self.bot.latency*1000)}ms")
        await m1.add_reaction('🏓')
        

    @botorowner()
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

    @botorowner()
    @commands.command(aliases=['botinfo', 'botstats', 'about'])
    async def stats(self, ctx:commands.Context):
        """Shows stats about the bot"""
        mem = psutil.virtual_memory()

        embed = discord.Embed(title="About:", colour=colour)
        embed.set_author(name=str(ctx.guild.owner), icon_url=ctx.guild.owner.avatar_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.description = "A bot for the DSCN discord made by [ItsArtemiz](https://discord.com/users/449897807936225290)"

        embed.add_field(name="Statistics",
                        value=f"<:server:789511925369274428> Server: {len(self.bot.guilds)}\n<:member:789445545915580486> Users: {len(self.bot.users)}\n\\⚙️ Commands: {len(self.bot.commands)}",
                        inline=False)

        embed.add_field(name="Usage",
                        value=f"<:cpu:789513513897951243> CPU: {psutil.cpu_percent()}%\n{mem[1] / 1000000} MB available ({(100 - mem[2]):.2f}%)",
                        inline=False)

        embed.add_field(name="Version",
                        value=f"<:python:789493535493718026> Python: {platform.python_version()}\n<:dpy:789493535501058078> Discord.py: {discord.__version__}\n\\🤖 Bot: v{version}",
                        inline=False)


        embed.set_footer(text=footer)

        await ctx.send(embed=embed)


    @botorowner()
    @commands.command(aliases=['ut'])
    async def uptime(self, ctx:commands.Context):
        """Shows bot uptime"""
        delta_uptime = datetime.utcnow() - self.bot.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        await ctx.send(f"I have been awake for: **{days}d, {hours}h, {minutes}m, {seconds}s**")
    
    @botorowner()
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.group(aliases=['artist'],invoke_without_command=True)
    async def artists(self, ctx:commands.Context):
        """Shows the registered artists"""
        embed = discord.Embed(colour=colour, title="All registered artists with DSCN", timestamp=datetime.utcnow())
        embed.set_footer(text=footer)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        text = ""
        gen = await self.artistDb.fetch_all
        async for a in gen:
            text += f"• **{a['name']}** - {a['music']} | [Latest Release]({a['latestTrack']})\n"

        embed.description = text

        await ctx.send(embed=embed)

    @commands.is_owner()
    @artists.command(aliases=['insert'])
    async def add(self, ctx:commands.Context, user:discord.Member, music:str, latestTrack:Optional[str]=None, trackUploaded:Optional[str]=None):
        """
        Adds the given member to the Artist Database

        Fields:
        • `<user>` - The discord member that needs to be added in the database
        • `<music>` - The music style of the artist, if it contains space, enlose them with quotes (i.e. "" or '')
        • `[latestTrack]` - The latest track of the artist released through the DSCN Label
        • `[trackUploaded]` - The time when it was uploaded. This should be of format **YYYY-MM-DD** (eg. 2020-12-12)
        
        If the `trackUploaded` is not provided, the current time is used
        """
        checkAll = await self.artistDb.fetch_all
        async for a in checkAll:
            if a['discordId'] == user.id:
                return await ctx.send(embed=discord.Embed(title=f"{user.name} is already registered with us", colour=discord.Colour.red()))
        
        name = user.display_name

        if trackUploaded is None:
            trackUploaded = datetime.utcnow()
        else:
            if isinstance(trackUploaded, str):
                newDate = trackUploaded.split("-")
                trackUploaded = datetime(int(newDate[0]), int(newDate[1]), int(newDate[2]))

            
        post = {"_id":0, "name":name, "discordId":user.id, "music":music, "latestTrack":latestTrack, "trackUploaded":trackUploaded}

        _404 = "https://i.kym-cdn.com/entries/icons/original/000/003/093/404.png"

        # embeds

        r = await self.artistDb.insert(post)

        if r:
            embed = discord.Embed(title="Artist Added Successfully", colour=discord.Colour.green(), timestamp=datetime.utcnow())
            embed.description = f"Added Artist **{name}** with music type **{music}**.\n[Latest Track]({latestTrack if latestTrack else _404}) | Uploaded: {trackUploaded}"
            embed.set_footer(text=f"Action by {ctx.author.name}")

        else:
            embed = discord.Embed(title="An Error Occured", colour=discord.Colour.red(), timestamp=datetime.utcnow())
            embed.description = f"The artist couldn't be added to the database. Add the following manually to the database:\nName: {name}\nId: {user.id}\nMusic: {music}\nlatestTrack: {latestTrack}\ntrackUploaded: {trackUploaded}"
            embed.set_footer(text=f"Action by {ctx.author.name}")

        await ctx.send(embed=embed)
        await self.LogChannel.send(embed=embed)

    @commands.is_owner()
    @artists.command(aliases=['modify', 'm'], usage="<field> <artist> [params...]")
    async def update(self, ctx:commands.Context, field:str, artist:discord.Member, *,param:str):
        """
        Used to update a field for the artist in the database

        Fields:
        • `<field>` - The field you want to update. There are currently 4 fields you can update:
            → name: updates the name of the artist which will be displayed on embeds. By default it is their server nickname
            → music: updates the music style of the artist
            → latestTrack: updates the lates track field. This also updates the track timestamp to the time of command usage
            → trackUploaded: updates when the track was uploaded
        
        • `<artist>` - The artist you want to update
        """
        old = {"discordId":artist.id}
        if field.lower() == "name":
            a = await self.artistDb.update(old, new={"name":param})
            if a:
                return await ctx.send(embed=discord.Embed(title=f"Name Succesfully updated to {param}", colour=discord.Color.green(), timestamp=datetime.utcnow()))
            else:
                return await ctx.send(embed=discord.Embed(title="An error occurred", colour=discord.Color.red()))
        
        elif field.lower() == "music":
            a = await self.artistDb.update(old, new={"music":param})
            if a:
                return await ctx.send(embed=discord.Embed(title=f"Music Type Succesfully updated to {param}", colour=discord.Color.green(), timestamp=datetime.utcnow()))
            else:
                return await ctx.send(embed=discord.Embed(title="An error occurred", colour=discord.Color.red()))
        elif field.lower() in ("latesttrack", "track"):
            a = await self.artistDb.update(old, new={"latestTrack":param})
            b = await self.artistDb.update(old, new={"trackUploaded":datetime.utcnow()})
            if a and b:
                return await ctx.send(embed=discord.Embed(title=f"Latest Track Succesfully updated to {param}", colour=discord.Color.green(), timestamp=datetime.utcnow()))
            else:
                return await ctx.send(embed=discord.Embed(title="An error occurred", colour=discord.Color.red()))
        elif field.lower() in ("trackuploaded","timestamp","uploaded"):
            new = param.split("-")
            a = await self.artistDb.update(old, new={"trackUploaded":datetime(int(new[0]), int(new[1]), int(new[2]))})
            if a:
                return await ctx.send(embed=discord.Embed(title=f"Music Type Succesfully updated to {param}", colour=discord.Color.green(), timestamp=datetime.utcnow()))
            else:
                return await ctx.send(embed=discord.Embed(title="An error occurred", colour=discord.Color.red()))

    @commands.is_owner()
    @artists.command(aliases=['d'])
    async def delete(self, ctx:commands.Context, artist:str):
        await ctx.send(f"Are you sure you want to delete the record for **{artist}**")

        def check(message:discord.Message):
            return ctx.author == message.author and ctx.channel == message.channel #and message.content.lower() == "yes"

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=30.0)
            if msg.content.lower() in ("yes", "y"):
                await ctx.send("Deleting records...")
                await self.artistDb.delete_one({"name":{"$eq":artist}})  
                return await ctx.send("Record deleted")
                
            elif msg.content.lower() in ("no", "n"):
                return await ctx.send("Phew, dodged a bullet there 😮")
            else:
                return await ctx.send("Cancelling command...")
                
        except asyncio.TimeoutError:
            return await ctx.send("Timeout reached. Cancelling command....")



            

def setup(bot:commands.Bot):
    bot.add_cog(Information(bot))