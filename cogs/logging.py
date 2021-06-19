from __future__ import annotations
from utils.bot import Bot
from utils.utils import log
import discord

from discord.ext import commands


class EventLogger(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    def embed_builder(
        self   
    ) -> discord.Embed:
        pass
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        pass