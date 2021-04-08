# -*- codingL utf-8 -*-

"""
MongoClient
~~~~~~~~~~~~

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

from utils.errors import NoCollectionGiven, NoDatabaseGiven
from motor import motor_asyncio
from typing import Iterable, Union
from pymongo.results import *
import os

from dotenv import load_dotenv
load_dotenv()

class MongoClient:
    def __init__(self, **kwargs) -> None:
        try:
            db = kwargs.get("db")
        except KeyError:
            db = kwargs.get("database")
        
        collection = kwargs.get("collection")

        if db is None:
            raise NoDatabaseGiven("No database was given.")
        if collection is None:
            raise NoCollectionGiven("No collection was given.")

        client = motor_asyncio.AsyncIOMotorClient(os.environ.get("DB_TOKEN"))
        db = client[db]
        self.collection = db[collection]

    async def insert_one(self, document:dict) -> InsertOneResult:
        """Inserts one document into the collection.

        Parameters
        ----------
        document : dict
            The document to insert.

        Returns
        -------
        InsertOneResult
            An instance of :class:`pymongo.results.InsertOne`
        """
        return await self.collection.insert_one(document)

    async def insert_many(self, documents:Iterable) -> InsertManyResult:
        """Inserts many documents into the collection.

        Parameters
        ----------
        documents : Iterable
            The different documents to append

        Returns
        -------
        InsertManyResult
            An instance of :class:`pymongo.results.InsertMany`
        """
        return await self.collection.insert_many(documents)

    async def find_one(self, filter:dict) -> Union[dict, None]:
        """Finds the document and returns it. If the document is not found, it returns `None`

        Parameters
        ----------
        filter : dict
            The filter to check while retrieving the document.

        Returns
        -------
        Union[dict, None]
            The document or `None` if not found.
        """
        return await self.collection.find_one(filter)

    def find(self, filter:dict={}, *args, **kwargs) -> motor_asyncio.AsyncIOMotorCursor:
        """Generates an `motor_asyncio.AsyncIOMotorCursor` returning many documents.

        Parameters
        ----------
        filter : Optional[dict]
            A filter to get certain type of documents. Defaults to {} returning every document in the collection.

        Returns
        -------
        motor_asyncio.AsyncIOMotorCursor
            The cursor returning the documents.
        """
        return self.collection.find(filter, *args, **kwargs)

    async def update_one(self, filter:dict, update:dict) -> UpdateResult:
        """Updates a single document in the collection. If many documents are found, it updates the first matching one.

        Parameters
        ----------
        filter : dict
            The filter to check for the documents.
        update : dict
            The new values to be set.

        Returns
        -------
        UpdateResult
            An instant of :class:`pymongo.results.UpdateResult`
        """
        return await self.collection.update_one(filter, update)

    async def update_many(self, filter:dict, update:dict) -> UpdateResult:
        """Updates all the document matching the filter.

        Parameters
        ----------
        filter : dict
            The filter to check for documents.
        update : dict
            The new values to be set.

        Returns
        -------
        UpdateResult
            An instance of :class:`pymongo.results.UpdateResult`
        """
        return await self.collection.update_many(filter, update)

    async def delete_one(self, filter:dict) -> DeleteResult:
        """Deletes a singe document from the collection based on the filter.

        Parameters
        ----------
        filter : dict
            The filter to check for the document.

        Returns
        -------
        DeleteResult
            An instance of :class:`pymongo.results.DeleteResult`
        """
        return await self.collection.delete_one(filter)

    async def delete_many(self, filter:dict) -> DeleteResult:
        """Deletes all documents matching the filter.

        Parameters
        ----------
        filter : dict
            The filter to check for the documents.

        Returns
        -------
        DeleteResult
            An instance of :class:`pymongo.results.DeleteResult`
        """
        return await self.collection.delete_many(filter)

    async def find_one_and_delete(self, filter:dict) -> Union[dict, None]:
        """Returns and delete the document matching the filter.

        Parameters
        ----------
        filter : dict
            The filter to check for the document.

        Returns
        -------
        dict
            The document deleted.
        """
        return await self.collection.find_one_and_delete(filter)

    async def count_documents(self, filter:dict={}, *args, **kwargs) -> int:
        """Returns the count of the documents depending on the filter.

        Parameters
        ----------
        filter : Optional[dict]
            This allows to get the count of certain type of documents, by default {} which returns all the documents in the collection.

        Returns
        -------
        int
            The count of the documents.
        """
        return await self.collection.count_documents(filter, *args, **kwargs)


    def find_one_and_update(self, filter:dict, update:dict, *args, **kwargs):
        pass