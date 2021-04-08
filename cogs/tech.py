# -*- codingL utf-8 -*-

"""
Techspiration Module
~~~~~~~~~~~~~~~~~~~~~

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

# This file is only concerned with the techspiration server.
# Guild ID: 756453096996995075


import os
from bot import DSCN
import discord
from discord.ext import tasks, commands
from random import choice
from datetime import datetime

class Techspiration(commands.Cog):
    def __init__(self, bot:DSCN):
        self.bot = bot
        self.send_tech_news.start()

    def get_country(self) -> str:
        return choice(["us","gb","in"])

    async def get_news(self) -> dict:
        url = f"http://newsapi.org/v2/top-headlines?country={self.get_country()}&category=technology&apiKey={os.environ.get('TECH_API_KEY')}"
        r = await self.bot.session.get(url)
        json = await r.json()

        _all = json['articles']
        news = choice(_all)

        return {
            'author':news['author'],
            'title':news['title'],
            'description':news['description'],
            'publisher':news['source']['name'],
            'content':news['content'],
            'publishedAt':datetime.strptime(news['publishedAt'],"%Y-%m-%dT%H:%M:%SZ"),
            'url':news['url'],
            'image':news['urlToImage']
        }


    async def create_news(self):
        news = await self.get_news()
        embed = discord.Embed(
            title = news['title'],
            url=news['url'],
            colour=discord.Colour.random(),
            timestamp=news['publishedAt']
        )
        embed.set_footer(text=f"{news['publisher']} | Published At")
        if news['author']:
            embed.set_author(name="Author: " + str(news['author']))
        description = news['description']
        if news['content']:
            description = description + "\n" + news['content']
        embed.description = description
        try:
            embed.set_image(url=news['image'])
        except:
            pass

        return embed

    @tasks.loop(hours=1.0)
    async def send_tech_news(self):
        channel = self.bot.get_channel(796435195879751681)
        if channel is None:
            channel = await self.bot.fetch_channel(796435195879751681)

        news = await self.create_news()
        try:
            await channel.send(embed=news)
        except:
            pass

    @send_tech_news.before_loop
    async def before_send_tech_news(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.send_tech_news.cancel()

        

def setup(bot:DSCN):
    bot.add_cog(Techspiration(bot))