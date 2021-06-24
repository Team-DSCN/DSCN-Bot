from __future__ import annotations
from datetime import datetime

import discord
import os
import random

from discord.ext import commands, tasks
from utils.bot import Bot

class News:
    def __init__(self, data: dict):
        self.author: str = data['author']
        self.title: str = data['title']
        self.description: str = data['description']
        self.publisher: str = data['source']['name']
        self.content: str = data['content']
        self.publishedAt = datetime.strptime(data['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        self.url: str = data['url']
        self.image: str = data['urlToImage']

class Tech(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.send_tech_news.start()
        
    def country(self) -> str:
        return random.choice(['us', 'uk', 'in'])
    
    
    async def get_news(self) -> News:
        url=f'http://newsapi.org/v2/top-headlines?country={self.country()}&category=technology&apiKey={os.environ.get("TECH_API_KEY")}'
        async with self.bot.session.get(url) as response:
            r = await response.json()
            try:
                news = random.choice(r['articles'])
            except IndexError:
                async with self.bot.session.get(url) as response:
                    r = await response.json()
                    news = random.choice(r['articles'])
            return News(news)
    
    async def create_news_embed(self) -> discord.Embed:
        news = await self.get_news()
        embed = discord.Embed(
            title = news.title,
            url = news.url,
            colour = discord.Colour.random(),
            timestamp = news.publishedAt
        )
        
        embed.set_footer(text=f'{news.publisher} | Published At')
        embed.set_author(name=f'Author: {news.author if news.author else "Unknown"}')
        embed.description = f'{news.description}\n{news.content}'
        
        try:
            embed.set_image(url=news.image)
        except:
            pass
        
        return embed
    
    
    @tasks.loop(hours=1.0)
    async def send_tech_news(self) -> None:
        webhook = discord.Webhook.from_url(url=os.getenv('TECH_NEWS_LOGGER'), session=self.bot.session)
        
        embed = await self.create_news_embed()
        
        await webhook.send(embed=embed)
        
    @send_tech_news.before_loop
    async def before_send(self) -> None:
        await self.bot.wait_until_ready()
        
    def cog_unload(self) -> None:
        self.send_tech_news.cancel()
        
def setup(bot: Bot):
    bot.add_cog(Tech(bot))