import asyncio
from datetime import datetime
import discord

from discord.ext import menus
from discord.ext.menus import First, Last

class RoboPages(menus.MenuPages, inherit_buttons=False):
    def __init__(self, source, *args, **kwargs):
        delete_message_after = kwargs.pop('delete_message_after', True)
        super().__init__(source, delete_message_after=delete_message_after, check_embeds=True, *args, **kwargs)
        self.input_lock = asyncio.Lock()
    
    async def finalize(self, timed_out):
        try:
            if timed_out:
                await self.message.clear_reactions()
            else:
                await self.message.delete()
        except discord.HTTPException:
            pass
        
    def _skip_when(self):
        return self.source.get_max_pages() <= 2
    
    def _skip_when_short(self):
        return self.source.get_max_pages() <=1
    
    async def remove_reaction(self, emoji, payload):
        user = self.bot.get_user(payload.user_id)
        try:
            await self.message.remove_reaction(emoji, user)
        except Exception as e:
            print(e)
        
    @menus.button('<:first:855373614642888714>', position=First(0), skip_if=_skip_when)
    async def rewind(self, payload):
        """Goes to first page."""
        await self.show_page(0)
        await self.remove_reaction('<:first:855373614642888714>', payload)

    @menus.button('<:previous:855373614299086859>', position=First(1), skip_if=_skip_when_short)
    async def back(self, payload):
        """Goes to the previous page."""
        await self.show_checked_page(self.current_page - 1)
        await self.remove_reaction('<:previous:855373614299086859>', payload)

    @menus.button('<:stop:855373614618116097>', position=First(2))
    async def stop_menu(self, payload):
        """Removes this message."""
        self.stop()
        await self.remove_reaction('<:stop:855373614618116097>', payload)

    @menus.button('<:next:855373615012380692>', position=Last(0), skip_if=_skip_when_short)
    async def forward(self, payload):
        """Goes to the next page."""
        await self.show_checked_page(self.current_page + 1)
        await self.remove_reaction('<:next:855373615012380692>', payload)

    @menus.button('<:last:855373614907129876>', position=Last(1), skip_if=_skip_when)
    async def fastforward(self, payload):
        """Goes to the last page."""
        await self.show_page(self._source.get_max_pages() - 1)
        await self.remove_reaction('<:last:855373614907129876>', payload)

    @menus.button('<:info:855373614625587241>', position=Last(2))
    async def show_information_page(self, payload):
        """Shows this message."""
        await self.remove_reaction('<:info:855373614625587241>', payload)
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

    @menus.button('<:number:855414332300591146>', position=Last(3), lock=False, skip_if=_skip_when)
    async def numbered_page(self, payload):
        """Lets you go to a page by typing its number."""
        if self.input_lock.locked():
            return
        
        async with self.input_lock:
            channel = self.message.channel
            author_id = payload.user_id
            to_delete = []
            to_delete.append(await channel.send('What page do you want to go?'))
            
            def check(msg: discord.Message):
                return msg.author.id == author_id and channel == msg.channel and msg.content.isdigit()
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=20.0)
            except asyncio.TimeoutError:
                to_delete.append(await channel.send('Took too long.'))
                await asyncio.sleep(5.0)
            else:
                page = int(msg.content)
                to_delete.append(msg)
                await self.show_checked_page(page - 1)
            finally:
                await self.remove_reaction('<:number:855414332300591146>', payload)
                
            try:
                await channel.delete_messages(to_delete)
            except Exception:
                pass
        
            
class ArtistEntry:
    def __init__(self, artist):
        self.name = artist.name
        self.music = artist.music
        self.playlist = artist.playlist
        self.added = artist.added
        self.avatar = artist.avatar

    def __str__(self) -> str:
        return (
            f'**Name:** {self.name}\n'
            f'**Music:** {self.music}\n'
            f'**With DSCN since:** {datetime.strftime(self.added, "%d/%m/%Y")}\n'
            f'**Playlist:** {self.playlist}'
        )

class ArtistPageSource(menus.ListPageSource):
    def __init__(self, entries, *, per_page=1):
        super().__init__(entries, per_page=per_page)
        
    async def format_page(self, menu: menus.Menu, entries):
        pages = []
        pages.append(str(entries))
        menu.embed.set_thumbnail(url=entries.avatar)
            
        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f'Page {menu.current_page+1}/{maximum} (Total {len(self.entries)} Artists)'
            menu.embed.set_footer(text=footer)
            
        menu.embed.description = '\n'.join(pages)
        return menu.embed
    
class ArtistPages(RoboPages):
    def __init__(self, entries, *, per_page=1):
        converted = [ArtistEntry(entry) for entry in entries]
        super().__init__(ArtistPageSource(converted, per_page=per_page))
        self.embed = discord.Embed(colour=0xce0037)