import asyncio
import discord

from discord.ext import menus
from discord.ext.menus import First, Last

class RoboPages(menus.MenuPages):
    def __init__(self, source, *, generate_page=True, **kwargs):
        delete_message_after = kwargs.pop('delete_message_after', True)
        super().__init__(source, delete_message_after=delete_message_after, **kwargs)
        self.info = False
        self._generate_page = generate_page
        for x in list(self._buttons):
            if ':' not in str(x):
                self._buttons(x)

    @menus.button('<:first:855373614642888714>', position=First(0))
    async def go_to_first_page(self, payload):
        """Goes to first page."""
        await self.show_page(0)

    @menus.button('<:previous:855373614299086859>', position=First(1))
    async def go_to_previous_page(self, payload):
        """Goes to the previous page."""
        await self.show_checked_page(self.current_page - 1)

    @menus.button('<:stop:855373614618116097>', position=First(2))
    async def stop_pages(self):
        """Removes this message."""
        self.stop()

    @menus.button('<:next:855373615012380692>', position=Last(0))
    async def go_to_next_page(self, payload):
        """Goes to the next page."""
        await self.show_checked_page(self.current_page + 1)

    @menus.button('<:last:855373614907129876>', position=Last(1))
    async def go_to_last_page(self, payload):
        """Goes to the last page."""
        await self.show_page(self._source.get_max_pages() - 1)

    @menus.button('<:info:855373614625587241>', position=Last(2))
    async def show_information_page(self, payload):
        """Shows this message."""
        embed = discord.Embed(
            title = 'Paginator Help',
            description= ' Hello! Welcome to the Help Page.',
            colour = 0xce0037
        )

        messages = []
        for (emoji, button) in self.buttons.items():
            messages.append(f'{emoji}: {button.action.__doc__}')

        embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)
        embed.set_footer(text=f'We were on page {self.current_page + 1}.')
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(20.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

    @menus.button('<:number:855414332300591146>', position=Last(3))
    async def numbered_page(self, payload):
        pass