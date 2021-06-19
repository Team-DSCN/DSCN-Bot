from datetime import datetime
from typing import List
import discord
import humanize

class Artist:
    def __init__(self, data: dict):
        self.name: str = data['name']
        self.music: str = data['music']
        self.playlist: str = data['playlist']
        self.avatar: str = data['avatar']
        self.added: datetime = data['added']
        self.searches: int = data.get('searches', 0)
        self.aliases: List[str] = data.get('aliases', [])
        
    def __repr__(self) -> str:
        return (f'<Artist name="{self.name}" music="{self.music}" added={self.added!r}'
                f' playlist="<{self.playlist}>" searches={self.searches} aliases={self.aliases!r}'
                f' avatar="<{self.avatar}>">'
        )
    
    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            colour = 0xce0037,
            timestamp = self.added
        )
        
        e.add_field(name='Name', value=self.name)
        e.add_field(name='Music', value=self.music)
        e.add_field(name='Playlist', value=self.playlist, inline=False)
        
        e.set_footer(text='With DSCN since')
        e.set_thumbnail(url=self.avatar)

        return e

def human_time(dt:datetime, **options) -> str:
    """Gives a nicely formated date object which is easy to read.
    Parameters
    ----------
    dt : datetime
        The datetime object we need to humanize.
    **options
        All valid arguments for `humanize.precisedelta`.
            minimum_unit: str   (default to seconds)
            suppress: tuple     (default to (), empty tuple)
            format: str         (default to %0.0f)
    Returns
    -------
    str
        The humanized datetime string.
    """
    minimum_unit = options.pop("minimum_unit", "seconds")
    suppress = options.pop("suppress", ())
    format = options.pop("format", "%0.0f")

    if dt is None:
        return 'N/A'
    return f"{humanize.precisedelta(discord.utils.utcnow() - dt, minimum_unit=minimum_unit, suppress=suppress, format=format)} ago"