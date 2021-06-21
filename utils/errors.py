from discord.ext import commands


class CollectionNotSet(Exception):
    pass

class NotBotChannel(commands.CheckFailure):
    def __init__(self, message=None, *args):
        if not message:
            message = (
                'The current channel is not whitelisted.'\
                ' Use the commands in a channel that is whitelisted.'
            )
        else:
            message = message
        super().__init__(message=message, *args)