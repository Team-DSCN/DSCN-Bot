
from utils.errors import NotBotChannel
from utils.context import Context
from discord.ext import commands

admin = commands.has_role(781796816257548308)
staff = commands.has_role(850669530661388288)
ar = commands.has_role(820579878826278932)

def botchannel():
    async def predicate(ctx: Context):
        if ctx.guild is None:
            raise commands.NoPrivateMessage('This command cannot be used in DMs.')
        settings = await ctx.bot.utils.find_one({'guildId':ctx.guild.id})
        if settings is None:
            return True
        if ctx.channel.id in settings.get('disabledChannels', []):
            raise NotBotChannel(f'Cannot use bot commands in #{ctx.channel.name} since it is not whitelisted.')
        return True
    return commands.check(predicate)