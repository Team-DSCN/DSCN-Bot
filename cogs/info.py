from __future__ import annotations

import discord

from discord.ext import commands
from utils.bot import Bot
from utils.context import Context
from utils.utils import human_time
from typing import Union, Optional

class Info(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command(aliases=['ui'])
    async def userinfo(self, ctx: Context, *, user: Optional[Union[discord.Member, discord.User]]):
        """ Gets info on a user. """
        user = user or ctx.author
        embed = discord.Embed(
            title = 'User Information',
            timestamp = discord.utils.utcnow()
        )
        embed.add_field(name='Name', value=str(user))
        embed.add_field(name='ID', value=f'`{user.id}`')
        embed.set_thumbnail(url=user.avatar.url)
        if isinstance(user, discord.Member):
            embed.colour = ctx.bot.colour
            embed.add_field(name='Nickname', value=user.nick)
            embed.add_field(name='Created At', value=human_time(user.created_at, minimum_unit='minutes'), inline=False)
            embed.add_field(name='Joined At', value=human_time(user.joined_at, minimum_unit='minutes'), inline=False)
            members: list = ctx.guild.members
            members.sort(key=lambda m: m.joined_at)
            embed.add_field(name='Join Position', value=members.index(user) + 1, inline=False)

            roles = user.roles
            roles.remove(ctx.guild.default_role)
            if roles:
                embed.add_field(
                    name = 'Roles',
                    value = ', '.join([r.mention for r in roles]) if len(roles) <= 7 else f'{len(roles)} roles',
                    inline = False
                )
        else:
            embed.set_author(name='This user is not in the server')

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(aliases=['si'])
    async def serverinfo(self, ctx: Context):
        pass
def setup(bot: Bot):
    bot.add_cog(Info(bot))