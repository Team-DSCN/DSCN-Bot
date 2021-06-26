"""
For Tech News in Techspiration Server
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
from datetime import datetime
from typing import Optional
import aiohttp

import discord
import os
import random

from discord.ext import commands, tasks
from utils.bot import Bot
from utils.cache import ExpiringCache

cache = ExpiringCache(seconds=7200)
key = 0
class News:
    def __init__(self, data: dict):
        source: dict = data['source']
        self.id: str | None = source.get('id', None)
        self.name: str = source.get('name', 'Unknown')
        self.author: str = data.get('author', 'Unknown')
        self.title: str = data['title']
        self.description: str = data['description']
        self.url: str = data['url']
        self.image_url: str = data.get('urlToImage', 'Unknown')
        self.published_at: datetime = datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        self.content: str = data['content']
    
    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=self.title,
            url=self.url,
            description=f'{self.description}\n{self.content}',
            colour=discord.Colour.random(),
            timestamp=self.published_at
        )
        
        e.set_author(name=f'Author: {self.author or "Unknown"}')
        e.set_footer(text=f'{self.name} | Published At')
        if self.image_url and self.image_url.startswith('http'):
            e.set_image(url=self.image_url)
            
        return e

class Tech(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.send_tech_news.start()

    def country(self) -> str:
        return random.choice(['us', 'uk', 'in'])
    
    async def get_news(self, *, use_cache=False) -> News | None:
        if use_cache and len(list(cache.values())) > 0:
            choice = random.choice(list(cache.values()))
            
            news = News(choice[0])
            return news
            
        global key
        headers = {'X-Api-key':os.environ.get('TECH_API_KEY')}
        url = f'https://newsapi.org/v2/top-headlines?country={self.country()}&category=technology'
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    l: list[dict] = r['articles']
                    
                    for item in l:
                        cache[key] = item
                        key+=1
                    if l is None and len(list(cache.values())):
                        l = list(cache.values())
                    else:
                        return
                    choice: dict = random.choice(l)
                    return News(choice)
            
    
    @tasks.loop(hours=1.0)
    async def send_tech_news(self) -> None:
        webhook = discord.Webhook.from_url(url=os.getenv('TECH_NEWS_LOGGER'), session=self.bot.session)
        try:
            news = await self.get_news()
        except IndexError:
            print('Index Error Occurred while sending the tech news.')
        if news:
            await webhook.send(embed=news.embed)
    
    @commands.has_role(773829273500909618) # Admin in Techspiration Server
    @commands.command(hidden=True)
    async def tech(self, ctx, channel:Optional[discord.TextChannel]):
        channel = channel or ctx.channel
        news = await self.get_news(use_cache=True)
        await channel.send(embed=news.embed)
        
    @send_tech_news.before_loop
    async def before_send(self) -> None:
        await self.bot.wait_until_ready()
        
    def cog_unload(self) -> None:
        self.send_tech_news.cancel()
        
def setup(bot: Bot):
    bot.add_cog(Tech(bot))