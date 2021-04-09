# -*- codingL utf-8 -*-

"""
Tags Module
~~~~~~~~~~~~~

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

from utils.paginator import TagPages
import discord

from bot import DSCN
from discord.ext import commands, menus
from utils.checks import STAFF, bot_channel
from typing import Union
from datetime import datetime
from difflib import get_close_matches

allowed_mentions = discord.AllowedMentions(
    everyone=False,
    users=False,
    roles=False,
    replied_user=True
)

class Tags(commands.Cog):
    def __init__(self, bot:DSCN):
        self.bot = bot
        
    async def get_tag(self, name:str) -> Union[dict, None]:
        """Gets the tag from the database.

        Parameters
        ----------
        name : str
            The name of the tag, can be the alias.

        Returns
        -------
        Union[str, None]
            The tag content or None if not found.
        """
        doc = await self.bot.tagdb.find_one({"$or":[{"name":{"$eq":name}}, {"aliases":{"$in":[name]}}]})
        if doc:
            return doc
        return None

    async def all_tags(self, name:str) -> bool:
        """Gets all the tags from the database and check if already exists.

        Parameters
        ----------
        name : str
            The name of the new tag to be created.

        Returns
        -------
        bool
            True if the tag already exists or False if they don't exist.
        """
        _all = []

        async for tag in self.bot.tagdb.find():
            _all.append(tag)

        for tag in _all:
            if tag["name"] == name:
                return True
            elif name in tag["aliases"]:
                return True
        else:
            return False

    async def create_tag(self, user:discord.Member, name:str, content:str) -> int:
        """Creates a tag.

        Parameters
        ----------
        user : discord.Member
            The user creating the tag.
        name : str
            The name of the tag.
        content : str
            The content of the tag.

        Returns
        -------
        int
            The id of the tag.
        """
        created = datetime.utcnow()
        doc = {
            "owner":user.id,
            "name":name,
            "content":content,
            "id":created.microsecond,
            "uses":0,
            "created":created,
            "aliases":[]
        }

        await self.bot.tagdb.insert_one(doc)
        return created.microsecond

    async def delete_tag(self, ctx:commands.Context, user:discord.User, name:str) -> discord.Message:
        """Delete a tag from the database.

        Parameters
        ----------
        ctx : commands.Context
            The context.
        user : discord.User
            The user invoking the command.
        name : str
            The name of the string.

        Returns
        -------
        discord.Message
            The Message sent.
        """
        tag = await self.get_tag(name)
        if tag is not None:
            if tag["owner"] == user.id:
                await self.bot.tagdb.delete_one({"name":{"$eq":name}})
                return await ctx.send("Successfully deleted the tag.")
            elif tag["owner"] in (449897807936225290, 393378646162800640, 488012130423930880):
                return await ctx.send("Can't delete a tag by another ADMIN.")
            elif STAFF in [r.id for r in ctx.author.roles]:
                await self.bot.tagdb.delete_one({"name":{"$eq":name}})
                return await ctx.send("Successfully deleted the tag.")
            else:
                return await ctx.send(f"You are not the owner of the tag: **{name}**")
        else:
            return await ctx.send(f"Cannot find the tag: **{name}**")

    
    async def create_alias(self, ctx:commands.Context, new_name:str, old_name:str) -> discord.Message:
        """Creates an alias for a command.

        Parameters
        ----------
        ctx : commands.Context
            The context.
        new_name : str
            The new name or alias of the tag.
        old_name : str
            The original name of the tag.

        Returns
        -------
        discord.Message
            The message sent.
        """
        tag = await self.get_tag(old_name)
        new = await self.get_tag(new_name)
        if (tag is not None) and (new is None):
            aliases:list = tag['aliases']
            if new_name in aliases:
                return await ctx.send("The alias already exists.")
            aliases.append(new_name)
            if tag["owner"] == ctx.author.id:
                await self.bot.tagdb.update_one({"name":{"$eq":old_name}}, {"$set":{"aliases":aliases}})
                return await ctx.send(f"Tag alias '{new_name}' that points to '{old_name}' successfully created.")
            else:
                return await ctx.send("You do not own the tag.")
        else:
            return await ctx.send(f"Cannot find the tag: **{old_name}**")

    def replied_reference(self, message) -> Union[discord.MessageReference, None]:
        """The message reference.

        Parameters
        ----------
        message : discord.Message
            The message for which the reference needs to be returnes

        Returns
        -------
        Union[discord.MessageReference, None]
            The message reference if it is a replied message or `None` if it is not.
        """
        ref = message.reference
        if ref and isinstance(ref.resolved, discord.Message):
            return ref.resolved.to_reference()
        return None

    async def tags_by_member(self, member:discord.Member, ctx:commands.Context) -> Union[discord.Message, None]:
        """Searches the database for a tag by a given member.

        Parameters
        ----------
        member : discord.Member
            The discord Member whose tags need to be searched for.
        ctx : commands.Context
            The command Context.

        Returns
        -------
        Union[discord.Message, None]
            The `Message` if no tags found else `None` if tags found, hence the menu was started.
        """
        _all = []
        tags = self.bot.tagdb.find({"owner":{"$eq":member.id}})
        async for t in tags:
            _all.append(t)

        if not _all:
            return await ctx.send(f"No tags created by **{member}**")
        else:
            menu = menus.MenuPages(TagPages(_all))
            await menu.start(ctx)


    @commands.group(invoke_without_command=True)
    async def tag(self, ctx:commands.Context, *, name:str):
        """ Shows a tag """

        tag = await self.get_tag(name)
        if tag is not None:
            e = discord.Embed(colour=0x2F3136, description=tag["content"], timestamp=datetime.utcnow(), allowed_mentions=allowed_mentions)
            e.set_footer(text=str(ctx.author))
            await ctx.send(embed=e, reference=self.replied_reference(ctx.message))
            await self.bot.tagdb.update_one({"name":{"$eq":name}}, {"$set":{"uses":tag["uses"]+1}})

        else:
            await ctx.send("Tag not found.")

    @bot_channel()
    @tag.command(aliases=["+"])
    async def create(self, ctx:commands.Context, name:str, *, content:commands.clean_content):
        """Creates a new tag."""
        cmds = ctx.command.parent.commands
        for c in cmds:
            if (name == c.name) or (name in c.aliases):
                return await ctx.send(f"**{name}** is a reserved keyword and cannot be used to make a new tag.")

        a = await self.all_tags(name)
        if a:
            return await ctx.send("A tag by that name already exists.")

        await self.create_tag(ctx.author, name=name, content=content)
        return await ctx.send(f"Successfully created the tag: {name}")
    
    @bot_channel()
    @tag.command(aliases=["-", "remove", "d"])
    async def delete(self, ctx:commands.Context, *, name:str):
        """ Deletes a tag. """
        await self.delete_tag(ctx, ctx.author, name=name)

    @bot_channel()
    @tag.command(usage="<new name> <old name>")
    async def alias(self, ctx:commands.Context, new_name:str, *, old_name:str):
        await self.create_alias(ctx=ctx, new_name=new_name, old_name=old_name)

    @bot_channel()
    @tag.command()
    async def info(self, ctx:commands.Context, *, name:str):
        """ Retrieves info on the tag. """
        tag = await self.get_tag(name=name)

        if tag:
            e = discord.Embed(
                title = name,
                colour = self.bot.colour,
                timestamp = tag["created"]
            )
            if name in tag["aliases"]:
                e.description = f"Alias of tag \"{tag['name']}\""
            owner_id = tag["owner"]
            user = (self.bot.get_user(owner_id)) or (await self.bot.fetch_user(owner_id))

            e.set_author(name=str(user), icon_url=user.avatar_url)
            e.add_field(name="Owner", value=user.mention)
            e.add_field(name="Uses", value=tag["uses"])
            e.add_field(name="Aliases", value=len(tag["aliases"]))
            e.set_footer(text="Tag created at")

            return await ctx.send(embed=e)
        else:
            return await ctx.send("Tag not found.")

    @bot_channel()
    @tag.command(hidden=True)
    async def aliases(self, ctx:commands.Context,*,name:str):
        """Shows all aliases of the tag."""

        tag = await self.get_tag(name=name)
        if tag:
            if tag["aliases"]:
                e = discord.Embed(
                    title = f"Aliases for tag `{tag['name']}`",
                    colour = self.bot.colour,
                    timestamp = tag["created"],
                    description = ", ".join([alias for alias in tag["aliases"]])
                )
                e.set_footer(text="Tag created at")
                return await ctx.send(embed=e)
            else:
                return await ctx.send("No aliases found for the given tag.")
        else:
            return await ctx.send("Tag not found.")

    @bot_channel()
    @tag.command()
    async def raw(self, ctx:commands.Context, *,name:str):
        """ Raw data of a tag. Escapes markdown and pings. """
        tag = await self.get_tag(name)
        if tag:
            e = discord.Embed(colour=0x2F3136, description=discord.utils.escape_markdown(tag["content"]), timestamp=datetime.utcnow(), allowed_mentions=allowed_mentions)
            e.set_footer(text=f"Raw Tag • {ctx.author}")
            await self.bot.tagdb.update_one({"name":{"$eq":name}}, {"$set":{"uses":tag["uses"]+1}})
            return await ctx.send(embed=e)
        else:
            return await ctx.send("Tag not found.")

    @bot_channel()
    @tag.command(aliases=["update", "modify"])
    async def edit(self, ctx:commands.Context, name:str, *, content:commands.clean_content):
        """ Updates an exisiting tag. """

        tag = await self.get_tag(name)
        if tag:
            if tag["owner"] == ctx.author.id:
                await self.bot.tagdb.update_one({"name":{"$eq":name}}, {"$set":{"content":content}})
                return await ctx.send("Successfully updated the content of the tag.")
            else:
                return await ctx.send("You can't edit the tag since you do not own it.")
        else:
            return await ctx.send("Tag not found.")

    @bot_channel()
    @tag.command(name="all")
    async def _all(self, ctx:commands.Context):
        """ Shows all tags """
        tags = []
        async for tag in self.bot.tagdb.find():
            tags.append(tag)
        
        menu = menus.MenuPages(TagPages(tags))
        await menu.start(ctx)

    @bot_channel()
    @tag.command()
    async def search(self, ctx:commands.Context, *, name:str):
        """ Searches for a tag. The query must be atleast 3 characters. """
        if len(name) < 3:
            return await ctx.send("The query must be atleast 3 characters long.")

        tags = []
        async for tag in self.bot.tagdb.find():
            tags.append(tag["name"])
            for t in tag["aliases"]:
                tags.append(t)

        matches = get_close_matches(name, tags)
        if not matches:
            return await ctx.send("Tag not found.")
        else:
            menu = menus.MenuPages(TagPages(matches))
            await menu.start(ctx)
        
    
    @bot_channel()
    @tag.command(name="list")
    async def _list(self, ctx:commands.Context, *, member:discord.Member=None):
        """ Shows tags created by the member. If member is not given, it shows tags created by the invokee of the command. """
        member = member or ctx.author
        await self.tags_by_member(member, ctx)

    @bot_channel()
    @commands.command()
    async def tags(self, ctx:commands.Context, *, member:discord.Member=None):
        """ An alias for tag list command. """
        member = member or ctx.author
        await self.tags_by_member(member, ctx)

def setup(bot:DSCN):
    bot.add_cog(Tags(bot))