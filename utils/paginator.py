# -*- codingL utf-8 -*-

"""
Paginator
~~~~~~~~~~~

Copyright (c) 2021 ItsArtemiz (Augadh Verma)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ItsArtemiz#8858 or https://discord.gg/2NVgaEwd2J

"""

from datetime import datetime
import discord
from discord.ext import menus

class ArtistEntry:
    def __init__(self, entry:dict) -> None:
        self.name = entry["name"]
        self.type = entry["type"]
        self.release = entry["release"]
        self.id = entry["discord_id"]

    def __str__(self) -> str:
        return f"・**{self.name}** *({self.type})*\n{self.release}"

    def __repr__(self) -> str:
        return f"<name={self.name}, type={self.type}, release={self.release}, discord_id={self.id}>"
    
    def __int__(self) -> int:
        return self.id

class ArtistPages(menus.ListPageSource):
    def __init__(self, entries, *, per_page=5):
        converted = []
        for entry in entries:
            converted.append(str(ArtistEntry(entry)))
        
        super().__init__(converted, per_page=per_page)

    async def format_page(self, menu, page):
        embed = discord.Embed(
            title="Showing all Artists with DSCN",
            colour = 0xce0037,
            description = "\n".join(item for item in page)
        ).set_footer(text="DSCN").set_thumbnail(url="https://cdn.discordapp.com/avatars/788766967472979990/b8bc50c3bd30f1e0099c65a7b26f3bc4.webp?size=1024")

        return embed


class TagPageEntry:
    def __init__(self, entry:dict) -> None:
        self.id:int = entry["id"]
        self.name:str = entry["name"]
        self.owner_id:int = entry["owner"]
        self.created:datetime = entry["created"]
        self.uses:int = entry["uses"]
        self.aliases:list = entry["aliases"]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id})"

    def __int__(self) -> int:
        return self.id

class TagPages(menus.ListPageSource):
    def __init__(self, entries, *, per_page=12):
        converted = []
        i = 1
        for entry in entries:
            if isinstance(entry, dict):
                converted.append(f"{i}. {TagPageEntry(entry=entry)}")
            elif isinstance(entry, str):
                converted.append(f"{i}. {entry}")
            i+=1
        
        super().__init__(converted, per_page=per_page)

    async def format_page(self, menu, page):
        e = discord.Embed(
            colour = 0xce0037,
            description = "\n".join(i for i in page)
        )

        return e