from discord.ext import commands
import re

async def check_perms(ctx:commands.Context, perms, *,check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved,name,None) == value for name, value in perms.items())

def has_perms(ctx:commands.Context, check=all, **perms):
    async def pred(ctx):
        return await check_perms(ctx, perms, check=check)
    return commands.check(pred)

async def check_guild_perms(ctx:commands.Context, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True
    if ctx.guild is None:
        return False
    
    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_guild_perms(*, check=all, **perms):
    async def pred(ctx:commands.Context):
        return await check_guild_perms(ctx, perms, check=check)
    return commands.check(pred)

def has_role(ctx:commands.Context, roleId:int):
    for role in ctx.author.roles:
        if role.id == roleId:
            return True
    return False

def has_either_role(ctx:commands.Context, roles:list):
    for role in ctx.author.roles:
        if role.id in roles:
            return True
    return False

def bot_channel():
    async def pred(ctx:commands.Context):
        pattern = re.compile(r'.bot-commands')
        if await ctx.bot.is_owner(ctx.author):
            return True
        if re.match(pattern, ctx.channel.name):
            return True
        return False
    return commands.check(pred)

def is_staff():
    async def pred(ctx:commands.Context):
        role = "staff"
        if await ctx.bot.is_owner(ctx.author):
            return True
        if role in [(role.name).lower() for role in ctx.author.roles]:
            return True
        return False
    return commands.check(pred)