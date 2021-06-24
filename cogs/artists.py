"""
Artists
Copyright (C) 2021  ItsArtemiz (Augadh Verma)

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
"""

from __future__ import annotations

import discord

from discord.ext import commands, menus
from difflib import get_close_matches
from typing import Optional

from utils.paginator import ArtistPages
from utils.bot import Bot
from utils.context import Context
from utils.flags import ArtistAdd, ArtistEdit
from utils.checks import admin, botchannel
from utils.utils import Artist

    
class Artists(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def get_artist(
        self, 
        ctx: Context, 
        name: str, 
        *, 
        to_return = False,
        update_search = False
    ) -> Artist | None:
        """Fetches the artist from the database. Because we need to search by name and it needs to be
        case insensitive, we are fetching all of them. I have no idea on how to search it otherwise.

        Parameters
        ----------
        ctx : Context
            The invocation context used to return a message of no artist is found.
        name : str
            The name of the artist searching for
        to_return : Optional[bool]
            Whether to return the "artist not found" message or not. By default `False`.
        update_search : Optional[bool]
            Updates the searches for the artist. By default `False`.

        Returns
        -------
        Union[Artist, None]
            The artist if found.
        """
        artists: list[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))

        async def do_update(a):
            await ctx.bot.artists.update_one(
                {'name':a.name},
                {'$set':{'searches':a.searches+1}}
            )

        for a in artists:
            if a.name.casefold() == name.casefold():
                if update_search:
                    await do_update(a)
                return a
            else:
                for alias in a.aliases:
                    if alias.casefold() == name.casefold():
                        if update_search:
                            await do_update(a)
                    return a
            
        else:
            if to_return:
                match = get_close_matches(name, [a.name for a in artists], 1)
                if match:
                    await ctx.send(f'Artist "{name}" not found. Did you mean "{match[0]}"?')
                else:
                    await ctx.send(f'Artist "{name}" not found.')
            return
    
    @botchannel()
    @commands.group(name='artist', invoke_without_command=True)
    async def artist(self, ctx: Context, *, name: str):
        """Shows an info"""
        artist = await self.get_artist(ctx, name, to_return=True, update_search=True)
        if not artist:
            return
        await ctx.send(embed=artist.embed)
        
    @admin()
    @artist.command(name='add')
    async def addartist(self, ctx: Context, *, flag: ArtistAdd):
        """Adds an artist."""
        artist = await self.get_artist(ctx, flag.name)
        if artist:
            return await ctx.send('Artist already exists!', embed=artist.embed)
        
        avatar = flag.avatar or ctx.guild.icon.url
        
        if isinstance(avatar, discord.User):
            avatar = avatar.avatar.url
        
        document = {
            'name':flag.name,
            'music':flag.music,
            'release':flag.release,
            'avatar':avatar,
            'added':discord.utils.utcnow(),
            'searches':0,
            'aliases':[]
        }
        
        await ctx.bot.artists.insert_one(document)
        
        await ctx.tick(True)
        await ctx.send(
            'Artist added successfully!',
            embed = Artist(document).embed
        )
        
    @admin()
    @artist.command(name='delete')
    async def delartist(self, ctx: Context, *, name: str):
        """Deletes an artist."""
        artist = await self.get_artist(ctx, name)
        if not artist:
            return await ctx.send(f'Artist "{name}" does not exist in our database.')
        
        await self.bot.artists.delete_one({'name':artist.name})
        await ctx.tick(True)
        
    @admin()
    @artist.command(name='modify', aliases=['edit', 'm', 'e'])
    async def editartist(self, ctx: Context, name, *, flag: ArtistEdit):
        """Modifies an artist."""
        artist = await self.get_artist(ctx, name, to_return=True)
        if not artist:
            return
        
        avatar = flag.avatar or artist.avatar
        
        if isinstance(avatar, discord.User):
            avatar = avatar.avatar.url        
        
        if not avatar.startswith('http'):
            return await ctx.send('Avatar url should start with "http(s)"!')
        
        if flag.aliases:
            aliases = flag.aliases.replace(', ', ',').replace(' ,', ',').split(',')
            aliases.extend(artist.aliases)
        else:
            aliases = artist.aliases
        aliases = list(set(aliases))
        for alias in aliases:
            if alias.startswith('-'):
                try:
                    aliases.remove(alias)
                    aliases.remove(alias.replace('-', ''))
                except ValueError:
                    pass
        
        document = {
            'name':flag.name or artist.name,
            'music':flag.music or artist.music,
            'release':flag.release or artist.release,
            'avatar':avatar,
            'added':artist.added,
            'searches':artist.searches,
            'aliases':aliases
        }
        
        await ctx.bot.artists.collection.replace_one({'name':artist.name}, document)
        artist = Artist(document)
        embed = artist.embed
        embed.title = 'Artist Modified Succesfully'
        embed.colour = discord.Color.green()
        embed.set_footer(text='Modified At')
        embed.timestamp = discord.utils.utcnow()

        if aliases:
            embed.add_field(name='Aliases', value=', '.join(aliases))
        
        await ctx.tick(True)
        await ctx.send(embed=embed)
        
    @botchannel()
    @artist.command(name='all')
    async def allartists(self, ctx: Context):
        """Shows all artists."""
        
        artists: list[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))
            
        artists.sort(key=lambda a: a.added)
        
        try:
            p = ArtistPages(artists)
        except menus.MenuError as e:
            await ctx.send(e)
        else:
            await p.start(ctx)
            
    @botchannel()
    @artist.command(name='popular')
    async def popartists(self, ctx: Context):
        """Shows artists based on most artist searches using the bot.
        
        This in no way represent the actual popularity of an artist and
        should not be used to compile any data for an artists popularity.
        """
        artists: list[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))
            
        artists.sort(key=lambda a: a.searches)
        
        try:
            p = ArtistPages(artists, show_searches=True)
        except menus.MenuError as e:
            await ctx.send(e)
        else:
            await p.start(ctx)
            
    @botchannel()
    @artist.command(aliases=['repr'], hidden=True)
    async def raw(self, ctx: Context, *, name:str):
        """Repr of the artist. If you know you know"""
        
        artist = await self.get_artist(ctx, name, to_return=True, update_search=True)
        if not artist:
            return
        await ctx.send(repr(artist))
    @botchannel()
    @commands.command()
    async def artists(self, ctx: Context, *, type:Optional[str]):
        """Shows all artists or popular artists depending on the type provided.
        By default shows all artists."""
        
        type = type or 'all'
        if type.casefold() == 'popular':
            await ctx.invoke(self.popartists)
        else:
            await ctx.invoke(self.allartists)
def setup(bot: Bot):
    bot.add_cog(Artists(bot))