from __future__ import annotations


import discord

from discord.ext import commands

from utils.errors import NotBotChannel
from utils.bot import Bot
from utils.context import Context
from utils.utils import command_usage

class ErrorHandler(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: commands.CommandError):
        # Inspired from EvieePy
        # Source: https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612
        
        if hasattr(ctx.command, 'on_error'):
            return # prevents cmds with local eh to be handled here.
        
        # Prevents any cogs with cog_command_error being handled here.
        cog: commands.Cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
    
        ignored = (commands.CommandNotFound, commands.NotOwner)
        
        error = getattr(error, 'original', error)
        
        if isinstance(error, ignored):
            return
        
        if isinstance(error, commands.DisabledCommand):
            if ctx.author.id == ctx.bot.owner_id:
                await ctx.reinvoke()
            else:
                return await ctx.send(f'{ctx.command} has been disabled.')
            
        elif isinstance(error, NotBotChannel):
            try:
                return await ctx.send(str(error))
            except discord.HTTPException:
                pass
            
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send(f'{ctx.command} can not be used in DMs')
            except discord.HTTPException:
                pass
            
        elif isinstance(error, (commands.UserNotFound, commands.MemberNotFound)):
            return await ctx.send(str(error))
        
        elif isinstance(error, commands.MissingPermissions):
            perms = ', '.join(f'`{p}`'.replace('_', ' ').upper() for p in error.missing_perms)
            return await ctx.send(f'You are missing some permissions: {perms}')
    
        elif isinstance(error, commands.BotMissingPermissions):
            perms = ', '.join(f'`{p}`'.replace('_', ' ').upper() for p in error.missing_perms)
            return await ctx.send(f'I am missing some permissions: {perms}')
        
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f'{ctx.command} is on a cooldown. Please retry after: {error.retry_after:.2f}')
        
        elif isinstance(error, commands.MissingRequiredFlag):
            return await ctx.send(f'Missing flag: **{error.flag.name}** in `{command_usage(ctx.command)}`')
        
        elif isinstance(error, commands.MissingFlagArgument):
            return await ctx.send(f'**{error.flag.name}** is missing an argument.')
        
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'Missing required argument: **{error.param.name}** in `{command_usage(ctx.command)}`')
            
        else:
            raise error
        
def setup(bot: Bot):
    bot.add_cog(ErrorHandler(bot))