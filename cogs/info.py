# -*- codingL utf-8 -*-

"""
Information Module
~~~~~~~~~~~~~~~~~~~

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
import time, platform

from utils.paginator import ArtistPages
from bot import DSCN
from datetime import datetime
from typing import List, Optional, Union
from discord.ext import commands, menus
from utils.checks import artist, bot_channel, staff


class Information(commands.Cog):
    def __init__(self, bot:DSCN):
        self.bot = bot

    def format_date(self, dt, **options) -> str:
        """Gives a nicely formated date object which is easy to read.

        Parameters
        ----------
        dt : datetime
            The datetime object we need to humanize.
        **options
            All valid arguments for `humanize.precisedelta`.
                minimum_unit: str   (default to seconds)
                suppress: tuple     (default to (), empty tuple)
                format: str         (default to %0.0f)

        Returns
        -------
        str
            The humanized datetime string.
        """
        minimum_unit = options.pop("minimum_unit", "seconds")
        suppress = options.pop("suppress", ())
        format = options.pop("format", "%0.0f")

        if dt is None:
            return 'N/A'
        return f"{dt:%Y-%m-%d %H:%M} ({humanize.precisedelta(datetime.utcnow() - dt, minimum_unit=minimum_unit, suppress=suppress, format=format)} ago)"

    @bot_channel()
    @commands.command(aliases=['ui','whois'])
    async def userinfo(self, ctx:commands.Context, *, user:Union[discord.User, discord.Member]=None) -> None:
        """Shows information about the user."""
        
        if not user:
            user = ctx.author

        e = discord.Embed(
            title="User Information",
            colour = self.bot.colour,
            timestamp = datetime.utcnow()
        )
        e.set_footer(text=self.bot.footer)

        e.set_author(name=str(user), icon_url=user.avatar_url, url=f"https://discord.com/users/{user.id}")

        e.add_field(name="ID", value=user.id)

        e.add_field(name="Created at", value=self.format_date(user.created_at, minimum_unit="hours"), inline=False)

        if isinstance(user, discord.Member):
            e.add_field(name="Joined at", value=self.format_date(user.joined_at, minimum_unit="hours"), inline=False)

            e.add_field(name="Roles", value=", ".join([r.mention for r in user.roles if r != ctx.guild.default_role] or ['None']))

        else:
            e.description = "*This user is not in the server.*"

        await ctx.send(embed=e)

    async def say_permissions(self, ctx:commands.Context, member:discord.Member, channel:discord.TextChannel):
        """Sends the permissions to the given context.

        Parameters
        ----------
        ctx : commands.Context
            The context where the bot will send the message.
        member : discord.Member
            The user whose permissions need to be sent.
        channel : discord.TextChannel
            The channel where the user's permission have to be extracted from.
        """

        perms = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour.value or self.bot.colour, timestamp=datetime.utcnow())
        e.set_author(name=str(member), icon_url=member.avatar_url, url=f"https://discord.com/users/{member.id}")
        e.set_footer(text=self.bot.footer)
        allowed, denied = [], []
        for name, value in perms:
            name = name.replace('_',' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name="Allowed", value="\n".join(allowed))
        e.add_field(name="Denied", value="\n".join(denied))

        await ctx.send(embed=e)

    @bot_channel()
    @commands.guild_only()
    @commands.command(aliases=['perms'])
    async def permissions(self, ctx:commands.Context, member:discord.Member=None, channel:discord.TextChannel=None):
        """Show's the members permissions in a specific channel.

        If no channelis given, it uses the current one.
        """

        channel = channel or ctx.channel
        member = member or ctx.author

        await self.say_permissions(ctx, member, channel)

    @bot_channel()
    @commands.guild_only()
    @commands.command(aliases=['si', 'guildinfo'])
    async def serverinfo(self, ctx:commands.Context):
        """ Shows info about the server. """

        guild:discord.Guild = ctx.guild

        if not guild.chunked:
            async with ctx.typing():
                await guild.chunk(cache=True)

        embed = discord.Embed(
            title=guild.name,
            description=f"**ID**: {guild.id}",
            timestamp=guild.created_at,
            colour=self.bot.colour
        )

        embed.set_footer(text="Created")

        if guild.icon:
            embed.set_thumbnail(url=guild.icon_url)


        key_to_emoji = {
            "text":"<:text:824903975626997771>",
            "voice":"<:voice:824903975098777601>"
        }

        text = len(guild.text_channels)
        voice = len(guild.voice_channels)

        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Voice Region", value=f"{guild.region}".title(), inline=True)
        embed.add_field(name="Channels", value=f"{key_to_emoji['text']} {text} {key_to_emoji['voice']} {voice}")
        embed.add_field(name="Roles", value=f"{len(guild.roles)} roles")
        embed.add_field(name="Emojis", value=f"{len(guild.emojis)} emojis")
        embed.add_field(name="Nitro Boost Count", value=f"{guild.premium_subscription_count} boosts (Level {guild.premium_tier})")
        if guild.features:
            embed.add_field(name="Features", value=", ".join(f"{f}".replace("_"," ").lower().title() for f in guild.features), inline=False)

        if guild.banner:
            embed.set_image(url=guild.banner_url)

        await ctx.send(embed=embed)

    @bot_channel()
    @commands.group(name="artist", aliases=["artists"], invoke_without_command=True)
    async def artist_group(self, ctx:commands.Context, *,artist:Union[discord.Member, str]=None):
        """Shows all the registered artist.
        
        If an artist is provided, it shows the info about the artist."""
        if artist is None:
            artists = []
            async for artist in self.bot.db.find():
                artists.append(artist)

            menu = menus.MenuPages(ArtistPages(artists))
            await menu.start(ctx)
        else:
            async def embed(doc:dict, artist:discord.User=None):
                e = discord.Embed(
                    colour = getattr(self, "colour", 0xce0037),
                    title = doc["name"],
                    description = f"**Music Style:** {doc['type']}"
                ).set_footer(text=self.bot.footer)
                e.add_field(name="Latest Release", value=doc['release'])
                e.set_thumbnail(url=artist.avatar_url if artist else "https://cdn.discordapp.com/avatars/788766967472979990/b8bc50c3bd30f1e0099c65a7b26f3bc4.webp?size=1024")
                await ctx.send(embed=e)

            if isinstance(artist, discord.Member):
                doc = await self.bot.db.find_one({"discord_id":{"$eq":artist.id}})
                if doc:
                    await embed(doc, artist)
                else:
                    return await ctx.send("Cannot seem to find the user with the given name.")
            elif isinstance(artist, str):
                doc = await self.bot.db.find_one({"name":{"$eq":artist}})
                if doc:
                    await embed(doc)
                else:
                    return await ctx.send("Cannot seem to find the user with the given name.")

    @staff()
    @artist_group.command(aliases=["+", "insert"])
    async def add(self, ctx:commands.Context, user:Optional[discord.Member], name:str, type:str, release:str=None):
        """ Adds an artist to the database.
        
        If the name of the artist contains space, use quotes, i.e. `""` or `''`.
        Fields:
        `user`: The discord User of the artist if they are in the discord. Can be a ping or their id. If they are not in the server, just leave this field.
        `name`: The name of the artist.
        `type`: The music type of the artist.
        `release`: The latest release of the artist.
        """
        user = user or ctx.author

        a = await self.bot.db.find_one({"name":{"$eq":name}})
        if a:
            return await ctx.send("Artist already registered.")

        d = {
            "discord_id":user.id,
            "name":name,
            "type":type,
            "release":release or "None registered."
        }

        await self.bot.db.insert_one(d)

        embed = discord.Embed(
            title="Successfully Added Artist",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=self.bot.footer)

        embed.add_field(name="Name", value=name)
        embed.add_field(name="Type", value=type)
        embed.add_field(name="Release", value=f"[{'Latest Release' if release else 'No release was registered'}]({release})")
        
        await ctx.send(embed=embed)

    @staff()
    @artist_group.command(aliases=["remove", "-", "d"])
    async def delete(self, ctx:commands.Context, *, name:str):
        """ Deletes an artist from the database. """

        artist = await self.bot.db.find_one_and_delete({"name":{"$eq":name}})
        if artist:
            embed = discord.Embed(
                title="Successfully Deleted Artist",
                colour=discord.Colour.green(),
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=self.bot.footer)
            embed.add_field(name="Name", value=artist["name"])
            embed.add_field(name="Type", value=artist["type"])
            embed.add_field(name="Release", value=artist["release"])

            return await ctx.send(embed=embed)

        else:
            return await ctx.send(f"No artist was found by the given name: **{name}**")

    @artist()
    @artist_group.command(aliases=["edit"])
    async def update(self, ctx:commands.Context, name:str, option:str, change:str):
        """ Updates an existing field to the new change.
        
        Fields:
        `option`: The field to modify. Must be either of: `type`, `release`.
                  To change your name, please request a Producer or a Manager.
        `change`: The modification to be made.
        """
        if option not in ("type","release","name"):
            return await ctx.send("Invalid option given.")
        doc = await self.bot.db.find_one({"name":{"$eq":name}})

        
        async def update():
            await self.bot.db.update_one({"name":{"$eq":name}}, {"$set":{option:change}})

        if doc:
            if doc["discord_id"] == ctx.author.id:
                if option == "name":
                    return await ctx.send("You cannot update the name.")
                await update()
            elif 781796816257548308 in [r.id for r in ctx.author.roles]:
                await update()
            elif self.bot.is_owner(ctx.author):
                await update()
            else:
                return await ctx.send("You cannot perform that action.")
        else:
            return await ctx.send("Cannot seem to find the user with the given name.")

    @bot_channel()
    @artist_group.command(name="releases")
    async def show_releases(self, ctx:commands.Context, *, name:Union[discord.User, str]):
        """ Shows all releases by an artist. """

        async def show_releases(doc:dict) -> None:
            e = discord.Embed(title=f"All Songs by {name if isinstance(name, str) else name.name}",
            colour=getattr(self.bot, "colour", 0xce0037)).set_footer(text=self.bot.footer)
            e.set_thumbnail(url=ctx.guild.icon_url)

            description = f'・{doc["release"]}\n' if doc["release"] != "None registered." else ""
            for url in doc["all"]:
                description += f"・{url}\n"

            e.description = description
            await ctx.send(embed=e)


        if isinstance(name, str):
            doc = await self.bot.db.find_one({"name":{"$eq":name}})
            if doc:
                await show_releases(doc)

        elif isinstance(name, discord.User):
            doc = await self.bot.db.find_one({"discord_id":{"$eq":name.id}})
            if doc:
                await show_releases(doc)

    @bot_channel()
    @commands.command()
    async def ping(self, ctx:commands.Context):
        """Shows the bot ping."""

        start = time.perf_counter()
        m:discord.Message = await ctx.send("Pinging...")
        end = time.perf_counter()
        duration = (end - start)*1000

        db_start = time.perf_counter()
        count = await self.bot.db.count_documents()
        db_end = time.perf_counter()
        db_duration = (db_end - db_start)*1000

        e = discord.Embed(
            colour = self.bot.colour
        )
        e.add_field(name="<a:typing:828718094959640616> | Typing", value=f"`{duration:.2f}ms`")
        e.add_field(name="<:stab:828715097407881216> | Websocket", value=f"`{(self.bot.latency*1000):.2f}ms`")
        e.add_field(name="<:mongo:814706574928379914> | Database", value=f"`{db_duration:.2f}ms`")

        await m.edit(content=None, embed=e)

    @bot_channel()
    @commands.command()
    async def botinfo(self, ctx:commands.Context):
        """ Shows bot info. """

        embed = discord.Embed(
            title = "Bot Info",
            colour = self.bot.colour,
            timestamp = datetime.utcnow()
        )
        embed.set_footer(text=self.bot.footer)
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        embed.add_field(
            name="Developer",
            value="[ItsArtemiz](https://discord.com/users/449897807936225290)"
        )
        embed.add_field(
            name="Python Version",
            value=platform.python_version()
        )
        embed.add_field(
            name="Discord.py Version",
            value=discord.__version__
        )
        embed.add_field(
            name="Bot Version",
            value=self.bot.version
        )
        embed.add_field(
            name="Server",
            value=platform.system()
        )

        embed.add_field(
            name="Total Commands",
            value=len(self.bot.commands)
        )

        await ctx.send(embed=embed)

    @bot_channel()
    @commands.command(aliases=["av"])
    async def avatar(self, ctx:commands.Context, *, user:Union[discord.User, discord.Member]=None):
        """ Shows avatar of a user. """
        user = user or ctx.author
        e = discord.Embed(
            colour = self.bot.colour,
            timestamp = datetime.utcnow()
        )
        e.set_footer(text=self.bot.footer)
        e.set_author(name=str(user), url=f"https://discord.com/users/{user.id}")
        e.set_image(url=user.avatar_url)

        await ctx.send(embed=e)

def setup(bot:commands.Bot):
    bot.add_cog(Information(bot))