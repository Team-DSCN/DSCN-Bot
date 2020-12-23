"""
This Discord Bot has been made to keep the server of DSCN Label safe and make it a better place for everyone.

Copyright © 2020 DSCN Label with ItsArtemiz (Augadh Verma). All rights reserved.

This Software is distributed with the GNU General Public License (version 3).
You are free to use this software, redistribute it and/or modify it under the
terms of GNU General Public License version 3 or later.

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of this Software.

This Software is provided AS IS but WITHOUT ANY WARRANTY, without the implied
warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

For more information on the License, check the LICENSE attached with this Software.
If the License is not attached, see https://www.gnu.org/licenses/

To contact us (DSCN Management), mail us at teamdscn@gmail.com
"""

import motor
import os

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = AsyncIOMotorClient(os.environ.get("DBToken"))

db = client['Artists']
# collection = db['Info']

class DatabaseConnection:
    def __init__(self, collection):
        self.collection:AsyncIOMotorClient = db[collection]

    @property
    async def count(self) -> int:
        """
        Returns the count of the artists in the database

        Type: `int`
        """
        return await self.collection.count_documents({})

    # <--- Fetch --->

    async def fetch(self, post:dict) -> dict:
        """
        Fetches one matching result from the database

        Type: `dict` or `None`
        """
        return await self.collection.find_one(post)

    @property
    async def fetch_all(self):
        """
        Returns all the records

        Type: `coro`
        """
        return self.collection.find({})

    @property
    async def fetch_last(self) ->dict:
        """
        Returns the last registered record

        Type: `dict`
        """
        a = await self.count
        return await self.fetch({"_id":{"$eq":a}})

    # <--- Insert --->

    async def insert(self, post:dict) -> bool:
        """
        Used to insert the data into the db

        Type: `bool`
        """
        count = await self.count
        if post['_id'] != count+1:
            post['_id'] = count+1

        try:
            await self.collection.insert_one(post)
            return True
        except:
            return False

    # <--- Delete --->

    async def delete_one(self, post:dict) -> bool:
        """
        Deletes the first matching entry based on the given dictionary

        Type: `bool`
        """
        try:
            await self.collection.delete_one(post)
            return True
        except:
            return False

    async def delete_many(self, post:dict) -> bool:
        """
        Deletes all the matching entries based on the given dictionary

        Type: `bool`
        """
        try:
            await self.collection.delete_many(post)
            return True
        except:
            return False

    # <--- Update --->

    async def update(self, old:dict, new:dict) -> bool:
        """
        Updates the old entry to the given new entry

        Type: `bool`
        """
        try:
            await self.collection.update_one(old, {"$set":new})
            return True
        except:
            return False