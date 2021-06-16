
from __future__ import annotations

import discord

from discord.ext import commands, tasks
from difflib import get_close_matches

from utils.bot import Bot
from utils.context import Context
from utils.flags import ArtistAdd
from utils.cache import ExpiringCache

class Artists(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cache = ExpiringCache(seconds=60, case_insensitive=True)
        self.update_artist.start()

    def cog_unload(self):
        self.update_artist.cancel()

    @tasks.loop(seconds=60)
    async def update_artist(self) -> None:
        async for document in self.bot.artists.find({}):
            self.cache[document['name']] = document

    @update_artist.before_loop
    async def before_artist_update(self) -> None:
        await self.bot.wait_until_ready()

    @commands.group(invoke_without_command=True)
    async def artist(self, ctx: Context, *, name:str):
        document = self.cache.get(name)
        if document is None:
            document = await ctx.bot.artists.find_one({'name':name})
            if document is None:
                artists = self.cache.keys()
                match = get_close_matches(name, artists, 1)
                if match:
                    return await ctx.send(f'Artist "{name}" not found. Did you mean "{match[0]}"')
                else:
                    return await ctx.send(f'Artist "{name}" not found.')
            else:
                self.cache[document['name']] = document
        else:
            document = document[0]
            
        embed = discord.Embed(
            colour = self.bot.colour,
            timestamp = document['added']
        )
        
        embed.add_field(name='Name', value=document['name'])
        embed.add_field(name='Music', value=document['music'])
        embed.add_field(name='Playlist', value=document['playlist'], inline=False)
        
        embed.set_footer(text='With DSCN since')
        embed.set_thumbnail(url=document['avatar'])
        await ctx.send(embed=embed)
    
    @commands.has_guild_permissions(administrator=True)
    @artist.command(name='add')
    async def add_artist(self, ctx:Context, *, flag: ArtistAdd):
        name = flag.name
        music = flag.music
        playlist = flag.playlist
        avatar = flag.avatar
        
        added = discord.utils.utcnow()
        
        if isinstance(avatar, discord.User):
            avatar = avatar.avatar.url
            
        if name in self.cache.keys():
            return await ctx.send('Artist with the given name already exists in our database.')
        
        document = {
            'name':name,
            'music':music,
            'playlist':playlist,
            'avatar':avatar,
            'added':added
        }
        await ctx.bot.artists.insert_one(document=document)
        self.cache[name] = document
        
        embed = discord.Embed(
            colour = discord.Colour.green(),
            title = 'Artist Added Successfully!',
            timestamp = added,
            description = f'**Name:** {name}\n'\
                          f'**Music:** {music}\n'\
                          f'**Playlist:** {playlist}'
        )
    
        embed.set_footer(text=f'Added by {ctx.author}', icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=avatar)
        
        await ctx.tick(True)
        await ctx.send(embed=embed)
        
def setup(bot: Bot):
    bot.add_cog(Artists(bot))