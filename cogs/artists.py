
from __future__ import annotations
import asyncio

import discord

from discord.ext import commands, tasks
from difflib import get_close_matches
from datetime import datetime
from typing import List, Union

from utils.bot import Bot
from utils.context import Context
from utils.flags import ArtistAdd, ArtistEdit
from utils.cache import ExpiringCache
from utils.checks import admin

class Artist:
    def __init__(self, data: dict):
        self.name: str = data['name']
        self.music: str = data['music']
        self.playlist: str = data['playlist']
        self.avatar: str = data['avatar']
        self.added: datetime = data['added']
        
    def __repr__(self) -> str:
        return f'<Artist name="{self.name}" music="{self.music}" added="{self.added}" playlist=<{self.playlist}>>'
    
    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            colour = 0xce0037,
            timestamp = self.added
        )
        
        e.add_field(name='Name', value=self.name)
        e.add_field(name='Music', value=self.music)
        e.add_field(name='Playlist', value=self.playlist, inline=False)
        
        e.set_footer(text='With DSCN since')
        e.set_thumbnail(url=self.avatar)

        return e
    
class Artists(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    async def get_artist(self, ctx: Context, name: str, *, to_return=False) -> Artist | None:
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

        Returns
        -------
        Union[Artist, None]
            The artist if found.
        """
        artists: List[Artist] = []
        async for document in ctx.bot.artists.find({}):
            artists.append(Artist(document))

        for a in artists:
            if a.name.casefold() == name.casefold():
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
        artist = await self.get_artist(ctx, name, to_return=True)
        if not artist:
            return
        await ctx.send(embed=artist.embed)
    
    @admin
    @artist.command(name='add')
    async def add_artist(self, ctx:Context, *, flag: ArtistAdd):
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
            'added':added
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
    @artist.command(name='modify', aliases=['edit', 'm', 'e'])
    async def artist_edit(self, ctx:Context, name:str, *, flag:ArtistEdit):
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
        
        document = {
            'name':flag.name or artist.name,
            'music':flag.music or artist.music,
            'playlist':flag.playlist or artist.playlist,
            'avatar':avatar or artist.avatar,
            'added':artist.added
        }
        
        await ctx.bot.artists.collection.replace_one({'name':artist.name}, document)
        artist = Artist(document)
        embed = artist.embed
        embed.title = 'Artist Modified Succesfully'
        embed.colour = discord.Color.green()
        embed.set_footer(text='Modified At')
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.tick(True)
        await ctx.send(embed=embed)
        
    @admin
    @artist.command(name='delete', aliases=['remove', 'd'])
    async def del_artist(self, ctx: Context, *, name:str):
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
        
def setup(bot: Bot):
    bot.add_cog(Artists(bot))