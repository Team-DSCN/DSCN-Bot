from __future__ import annotations

import discord

from utils.errors import NotBotChannel
from utils.context import Context
from discord.ext import commands

owner = {449897807936225290, 488012130423930880, 393378646162800640}

REPRESENTATIVE = 781796816257548308
STAFF = 850669530661388288
AR = 820579878826278932

def has_any_role(member: discord.Member, roles: list[int]) -> bool:
    
    if not isinstance(member, discord.Member):    
        raise TypeError(f'Instance of discord.Member expected, got {member.__class__.__name__}')
    member_roles: list[int] = [r.id for r in member.roles]
    for role in roles:
        if role in member_roles:
            return True
    else:
        return False

def admin():
    def predicate(ctx: Context):
        if ctx.author.id in owner:
            return True
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        else:
            return has_any_role(ctx.author, [REPRESENTATIVE])
        
    return commands.check(predicate)

def staff():
    def predicate(ctx: Context):
        if ctx.author.id in owner:
            return True
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        else:
            return has_any_role(ctx.author, [REPRESENTATIVE, STAFF])
        
    return commands.check(predicate)

def ar():
    def predicate(ctx: Context):
        if ctx.author.id in owner:
            return True
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        else:
            return has_any_role(ctx.author, [REPRESENTATIVE, STAFF, AR])
        
    return commands.check(predicate)

def botchannel():
    async def predicate(ctx: Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage('This command cannot be used in DMs.')
        settings = await ctx.bot.settings.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return True
        if ctx.channel.id in settings.get('disabledChannels', []):
            raise NotBotChannel(f'Cannot use bot commands in #{ctx.channel.name} since it is not whitelisted.')
        return True
    return commands.check(predicate)