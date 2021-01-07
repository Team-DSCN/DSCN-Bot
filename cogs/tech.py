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

# This file is only concerned with the techspiration server.
# Guild ID: 756453096996995075

import discord
import random
import os
from discord.ext import commands, tasks
from discord.utils import get
from datetime import datetime

from utils.checks import bot_channel
from utils.requests import Requests

class Techspiration(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.requests = Requests()
        self.latest_tech_news.start()


    def get_country(self) -> str:
        l = ["in","gb","us"]
        return random.choice(l)

    async def get_news(self) -> dict:
        country = self.get_country()
        r = (await self.requests.get(f"http://newsapi.org/v2/top-headlines?country={country}&category=technology&apiKey={os.environ.get('NewsAPIKey')}"))['json']
        ch = random.choice(r['articles'])

        return {
            "source_name":ch['source']['name'],
            "author":ch['author'],
            "title":ch['title'],
            "description":ch['description'],
            "title_url":ch['url'],
            "image_url":ch['urlToImage'],
            "content":ch['content'],
            "published_at":ch['publishedAt']
        }


    async def random_colour(self) -> int:
        c = (await self.requests.get("http://www.colr.org/json/color/random"))['hex']
        return int(c,16)

    def convert_time(self, time) -> datetime:
        return datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")

    @tasks.loop(minutes=5.0)
    async def latest_tech_news(self):
        channel:discord.TextChannel = self.bot.get_channel(796435195879751681)
        if channel is not None:
            news = await self.get_news()
            embed = discord.Embed(title=news['title'], url=news['title_url'], colour=self.random_colour(), timestamp=self.convert_time(news['published_at']))
            description = news['description']
            content = news['content']
            
            if content:
                description = description + "\n" + content
            
            embed.description = description
            
            if news['image_url']:
                embed.set_image(url=news['image_url'])
            
            if news['source_name']:
                source_name=news['source_name'] + " | Published At"
            else:
                source_name = "Published At"
            embed.set_footer(text=source_name)

            await channel.send(embed=embed)
    
    @latest_tech_news.before_loop
    async def before_news(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.latest_tech_news.cancel()

def setup(bot:commands.Bot):
    bot.add_cog(Techspiration(bot))