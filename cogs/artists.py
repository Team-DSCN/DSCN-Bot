
from __future__ import annotations
import asyncio
from utils.paginator import ArtistPages

import discord

from discord.ext import commands, menus, tasks
from difflib import get_close_matches
from datetime import datetime
from typing import List, Union

from utils.bot import Bot
from utils.context import Context
from utils.flags import ArtistAdd, ArtistEdit
from utils.checks import admin
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
        artists: List[Artist] = []
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
    
    @commands.group(invoke_without_command=True)
    async def artist(self, ctx: Context, *, name:str):
        """Shows info about an artist."""
        artist = await self.get_artist(ctx, name, to_return=True, update_search=True)
        if not artist:
            return
        await ctx.send(embed=artist.embed)
    
    @admin
    @artist.command(
        name='add',
        usage='flags(name: <name> music: <music style> playlist: <YouTube playlist> avatar: [User | str])'
    )
    async def add_artist(self, ctx:Context, *, flag: ArtistAdd):
        """Adds an artist to the database.
        
        Note: The flags don't have a specific order."""
        artist = await self.get_artist(ctx, flag.name)
        if artist:
            await ctx.send(f'Artist "{flag.name}" is already registered with us:\n{artist}')
            return
        
        avatar = flag.avatar
        if isinstance(avatar, discord.User):
            avatar = avatar.avatar.url
            
        added = discord.utils.utcnow()
        
        document = {
            'name':flag.name,
            'music':flag.music,
            'playlist':flag.playlist,
            'avatar':avatar,
            'added':added,
            'aliases':[],
            'searches':0
        }
        
        await ctx.bot.artists.insert_one(document)
        artist = Artist(document)
        
        embed = artist.embed
        
        embed.colour = discord.Colour.green()
        embed.title = 'Artist Added Succesfully'
        embed.set_footer(text=ctx.footer, icon_url=ctx.author.avatar.url)
        
        await ctx.tick(True)
        await ctx.send(embed=embed)
        
    @admin
    @artist.command(
        name='modify', 
        aliases=['edit', 'm', 'e'],
        usage='<name> flags(name: [new name] music: [music] playlist: [YouTube playlist] avatar: [User | str] aliases: [name1, name2])'
    )
    async def artist_edit(self, ctx:Context, name:str, *, flag:ArtistEdit):
        """Modifies field(s) for the artist in our database."""
        artist = await self.get_artist(ctx, name, to_return=True)
        if not artist:
            return
        if artist.avatar and flag.avatar is None:
            avatar = artist.avatar
        else:
            avatar = flag.avatar
        
        if isinstance(avatar, discord.User):
            avatar = avatar.avatar.url
        
        if not avatar.startswith('http'):
            return await ctx.send('Invalid avatar given. Avatars must start with "http(s)". You may also give a discord user.')

        if flag.aliases:
            aliases = flag.aliases.replace(', ', ',').replace(' ,', ',').split(',')
            aliases.extend(artist.aliases)
        else:
            aliases = artist.aliases

        aliases = list(set(aliases))
        
        document = {
            'name':flag.name or artist.name,
            'music':flag.music or artist.music,
            'playlist':flag.playlist or artist.playlist,
            'avatar':avatar or artist.avatar,
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

        embed.add_field(name='Aliases', value=', '.join(aliases))
        
        await ctx.tick(True)
        await ctx.send(embed=embed)
        
    @admin
    @artist.command(name='delete', aliases=['remove', 'd'])
    async def del_artist(self, ctx: Context, *, name:str):
        """Deletes an artist from the database."""
        artist = await self.get_artist(ctx, name, to_return=True)
        if not artist:
            return
        
        await ctx.send('Are you sure you want to delete the artist? (Y/N)\nSay `cancel` to abort.', embed=artist.embed)
        
        def check(msg: discord.Message):
            return msg.channel == ctx.channel and msg.author == ctx.author
        
        try:
            msg:discord.Message = await self.bot.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            return await ctx.send('Took to long to answer. Aborting...')
        else:
            if msg.content.lower() in ('yes', 'y'):
                await ctx.bot.artists.delete_one({'name':artist.name})
                await ctx.tick(True)
                await ctx.send('Successfully Deleted the Artist.')
            elif msg.content.lower() in ('no', 'n', 'cancel', 'abort'):
                return await ctx.send('Aborting...')
            else:
                return await ctx.send('Invalid option provided. Aborting...')
            
    @artist.command(name='all')
    async def all_artists(self, ctx:Context):
        """Shows all the artists with DSCN"""
        artists: List[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))

        def key(a):
            return a.added

        artists.sort(key=key)
            
        try:
            p = ArtistPages(artists)
        except menus.MenuError as e:
            await ctx.send(e)
        else:
            await p.start(ctx)

    @artist.command(name='popular', hidden=False)
    async def popular_artists(self, ctx:Context):
        """Shows artists based on most artist searches using the bot.
        
        This in no way represent the actual popularity of an artist and
        should not be used to compile any data for an artists popularity."""
        artists: List[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))

        def key(a: Artist):
            return a.searches

        artists.sort(key=key, reverse=True)

        try:
            p = ArtistPages(artists, show_searches=True)
        except menus.MenuError as e:
            await ctx.send(e)
        else:
            await p.start(ctx)

    @artist.command(name='raw', aliases=['repr'], hidden=True)
    async def reprartist(self, ctx: Context, *, name:str):
        """If you now you know"""
        artist = await self.get_artist(ctx, name, to_return=True)
        if not artist:
            return
        await ctx.send(repr(artist))
        
def setup(bot: Bot):
    bot.add_cog(Artists(bot))