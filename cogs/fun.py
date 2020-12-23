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

import discord, json, aiohttp, io

from discord.ext import commands
from datetime import datetime
from utils.utils import Checks, Requests


from jishaku.codeblocks import codeblock_converter

with open("utils/vars.json") as f:
    data = json.load(f)

footer = data['footer']
colour = int(data['colour'],16)


botcmdchannel = Checks().botcmdchannel
botorowner = Checks().botorowner


class Fun(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.requests = Requests()

    @commands.is_owner()
    @commands.command(name="eval", aliases=['e'], hidden=True)
    async def evalCode(self, ctx:commands.Context, *, code:str):
        """Evaluates code"""
        jishaku_cog = self.bot.get_cog("Jishaku")
        arg = codeblock_converter(code)

        await jishaku_cog.jsk_python(ctx, argument=arg)

    @commands.is_owner()
    @commands.command(name="say", hidden=True)
    async def saySomething(self, ctx:commands.Context, *, content:str):
        """Says something on your behalf"""
        await ctx.message.delete()
        await ctx.send(content)

    @commands.is_owner()
    @commands.command(name="screenshot", aliases=['ss'], hidden=True)
    async def ssUrl(self, ctx:commands.Context, url:str):
        embed = discord.Embed(title=f"Screenshot of {url}", colour=colour)
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://image.thum.io/get/width/1920/crop/675/maxAge/1/noanimate/{url}') as r:
                read = await r.read()
        embed.set_image(url="attachment://ss.png")
        embed.set_footer(text=footer)

        await ctx.send(file=discord.File(io.BytesIO(read), filename="ss.png"), embed=embed)
    
    @botorowner()
    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @commands.command(name="chatbot", aliases=["cb"])
    async def chatBot(self, ctx:commands.Context, *, message:str):
        """Used to talk with a chatbot"""
        data = await self.requests.get(f"http://bruhapi.xyz/cb/{message}")
        await ctx.send(data['json']['res'])

    @botorowner()
    @commands.cooldown(2, 5, commands.cooldowns.BucketType.user)
    @commands.command(name="translate", aliases=['tr'])
    async def translate(self, ctx:commands.Context, *,message:str):
        """Used to translate a given word to english.
        ⚠ Might not give the output you deserve"""
        data = await self.requests.get(f"http://bruhapi.xyz/translate/{message}")
        await ctx.send(f"`{message}` translates to **`{data['json']['text']}`**.\n*Detected Language: {data['json']['lang']}*")

    @botorowner()
    @commands.group(name="random", aliases=['rand'])
    async def rand(self, ctx:commands.Context):
        """Some random stuff"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @rand.command()
    async def word(self, ctx):
        """Gives a random word"""
        data = await self.requests.get("http://bruhapi.xyz/word")
        await ctx.send(f"A random word is: **`{data['json']['res']}`**")

    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @rand.command()
    async def topic(self, ctx):
        """Gives a random topic to talk on"""
        data = await self.requests.get("http://bruhapi.xyz/topic")
        await ctx.send(data['json']['res'])

    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @rand.command()
    async def fact(self, ctx):
        """Gives a random fact"""
        data = await self.requests.get("http://bruhapi.xyz/fact")
        await ctx.send(data['json']['res'])
    
    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @rand.command()
    async def joke(self, ctx):
        """A joke. That's it."""
        data = await self.requests.get(f"http://bruhapi.xyz/joke")
        await ctx.send(data['json']['res'])

    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @rand.command()
    async def dadjoke(self, ctx):
        """A dadjoke"""
        data = await self.requests.get("https://dadjoke-api.herokuapp.com/api/v1/dadjoke")
        await ctx.send(data['json']['joke'])
        
    @botorowner()
    @commands.cooldown(2,5, commands.cooldowns.BucketType.user)
    @commands.command(name="image")
    async def generateImage(self, ctx, *, message:str):
        """Generates an image based on text"""
        embed = discord.Embed(colour=colour)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://tti.wumpus.dev/tti/{message}") as r:
                read = await r.read()
        embed.set_image(url="attachment://image.png")
        embed.set_footer(text=footer)

        await ctx.send(file=discord.File(io.BytesIO(read), filename="image.png"), embed=embed)

    @botorowner()
    @commands.command(name="poll")
    async def makePoll(self, ctx:commands.Context, title:str, *options):
        """Makes a quick poll"""
        if len(options)>10:
            return await ctx.send("You can have a maximum of 10 options.")
        elif len(options)<2:
            return await ctx.send("You need to provide atleast 2 options.")

        reactions = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"}
        s = ""
        num = 1
        for i in options: 
            s += f"{num} - {i}\n" 
            num += 1
        embed = discord.Embed(title=title, description=s, colour=colour)
        embed.set_footer(text=footer)
        try:
            await ctx.channel.purge(limit=1)
        except:
            pass
        msg = await ctx.send(embed=embed)
        for i in range(1, len(options) + 1): await msg.add_reaction(reactions[i])

def setup(bot:commands.Bot):
    bot.add_cog(Fun(bot))