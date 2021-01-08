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

import discord, json, os
import random

from discord.ext import commands, tasks
from datetime import datetime

with open("utils/vars.json") as f:
    data = json.load(f)

colour = int(data['colour'], 16)
footer = data['footer']

class Config(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.changePresence.start()

    '''
    @commands.is_owner()
    @commands.command(name="prefix")
    async def changePrefix(self, ctx:commands.Context, newPrefix:str):
        """
        Used to change the prefix of the bot
        """
        f = open("utils/vars.json", "r")
        data = json.load(f)
        temp = data['prefix']
        data['prefix'] = f"{newPrefix}"
        f.close()
        f2 = open("utils/vars.json", "w")
        json.dump(data, f2, indent=4)
        await ctx.send(f"Prefix was changed from {temp} to {newPrefix}")
    '''

    @commands.is_owner()
    @commands.command(name="load")
    async def loadCog(self, ctx:commands.Context, name:str):
        """Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📥 Loaded extension: **`cogs/{name}.py`**")

    @commands.is_owner()
    @commands.command(name="unload")
    async def unloadCog(self, ctx:commands.Context, name:str):
        """ Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📤 Unloaded extension: **`cogs/{name}.py`**")

    @commands.is_owner()
    @commands.command(name="reload")
    async def reloadCog(self, ctx:commands.Context, name:str):
        """ Reloads an extension. """
        if name != "all":
            try:
                self.bot.reload_extension(f"cogs.{name}")
            except Exception as e:
                return await ctx.send(f"```py\n{e}```")
            await ctx.send(f"🔁 Reloaded extension: **`cogs/{name}.py`**")

        if name == "all":
            for f in os.listdir("cogs"):
                if f.endswith(".py"):
                    name = f[:-3]
                    try:
                        self.bot.reload_extension(f"cogs.{name}")
                    except Exception as e:
                        return await ctx.send(f"```py\n{e}```")
            await ctx.send("🔁 Reloaded all extensions.")
            
    @commands.is_owner()
    @commands.command(name="cogs")
    async def allCogs(self, ctx:commands.Context):
        """
        Displays all active cogs.
        """
        embed = discord.Embed(
            title = "All Currently Active Cogs",
            description = "\n".join([cog for cog in self.bot.cogs.keys()]),
            colour = colour,
            timestamp = datetime.utcnow()
        )

        embed.set_footer(text=footer, icon_url=ctx.guild.icon_url)

        await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.group()
    async def status(self, ctx:commands.Context):
        """Changes the status of the bot"""
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @status.command()
    async def playing(self, ctx, *, status:str):
        """Sets the status to playing"""
        member:discord.Member = ctx.guild.get_member(self.bot.user.id)
        current = member.status
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status), status=current)
        await ctx.send(f"Successfully changed to: **`Playing {status}`**")
    
    @status.command()
    async def watching(self, ctx, *, status:str):
        """Sets the status to watching"""
        member:discord.Member = ctx.guild.get_member(self.bot.user.id)
        current = member.status
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status), status=current)
        await ctx.send(f"Successfully changed to: **`Watching {status}`**")

    @status.command()
    async def listening(self, ctx, *, status:str):
        """Sets the status to listening"""
        member:discord.Member = ctx.guild.get_member(self.bot.user.id)
        current = member.status
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status), status=current)
        await ctx.send(f"Successfully changed to: **`Listening to {status}`**")

    @status.command()
    async def competing(self, ctx, *,status:str):
        """Sets the status to competing"""
        member:discord.Member = ctx.guild.get_member(self.bot.user.id)
        current = member.status
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=status), status=current)
        await ctx.send(f"Successfully changed to: **`Competing {status}`**")


    @status.command(name="type")
    async def act(self, ctx, activity:str=None):
        """Changes the activity state"""
        member:discord.Member = ctx.guild.get_member(self.bot.user.id)
        current = member.activity

        types = "• `online`\n• `idle`\n• `dnd`\n• `offline`"
        if activity is None or activity.lower() == "online":
            await self.bot.change_presence(status=discord.Status.online, activity=current)
            await ctx.send(f"Successfully changed the bot's state to: **`Online`**")
        elif activity.lower() == "idle":
            await self.bot.change_presence(status=discord.Status.idle, activity=current)
            await ctx.send(f"Successfully changed the bot's state to: **`Idle`**")
        elif activity.lower() == "dnd":
            await self.bot.change_presence(status=discord.Status.dnd, activity=current)
            await ctx.send(f"Successfully changed the bot's state to: **`Do Not Disturb`**")
        elif activity.lower() == "offline" or activity.lower() == "invisible":
            await self.bot.change_presence(status=discord.Status.offline, activity=current)
            await ctx.send(f"Successfully changed the bot's state to: **`Offline`**")
        else:
            await ctx.send(f"Invalid option was provided. Please provide one of the following options: \n{types}")
        

    async def get_activity(self):
        l = [
            "Sahara by BENZOD",
            "Retrograde by Rag",
            "Can You Hear The Water Run? by Hriday",
            "Sakura by JG Keeper"
        ]

        return random.choice(l)

    @tasks.loop(minutes=5.0)
    async def changePresence(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivtyType.listening, name=await self.get_activity()))

    @changePresence.before_loop
    async def before_change(self):
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.changePresence.cancel()

def setup(bot:commands.Bot):
    bot.add_cog(Config(bot))