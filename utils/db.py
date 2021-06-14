"""
MongoClient - Connects with MongoDB
Copyright (C) 2021  ItsArtemiz (Augadh Verma)

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
"""

from __future__ import annotations

from typing import Iterable, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorCursor
from pymongo.results import (
    BulkWriteResult,
    DeleteResult,
    InsertManyResult,
    InsertOneResult,
    UpdateResult
)

class Client:
    def __init__(self, uri: str, db: str, collection: str, *, tz_aware=True, connect=True, **kwargs):
        """Client for a MongoDB Operations.

        Parameters
        ----------
        uri : str
            The URI or the host used to log into MongoDB.
        db : str
            The database to access.
        collection : str
            The collection of the database to access.
        tz_aware : Optional[bool]
            :class:`datetime.datetime` instances returned as values in a document by this
            :class:`Client` will be timezone aware (otherwise they will be naive), by default `True`.
        connect : Optional[bool]
            If `True` (the default), the :class:`Client` will immediately begin connecting to
            MongoDB in the background. Otherwise connect on the first operation.
        """
        client = AsyncIOMotorClient(uri, tz_aware=tz_aware, connect=connect, **kwargs)
        db = client[collection]
        self.collection = db[collection]

    @property
    def collection(self) -> AsyncIOMotorCollection:
        """The collection initiated for the client.

        Returns
        -------
        AsyncIOMotorCollection
            The collection.
        """
        return self.collection

    async def insert_one(self, document: dict, **kwargs) -> InsertOneResult:
        """Inserts a document into the collection.

        Parameters
        ----------
        document : dict
            The document to insert.

        Returns
        -------
        InsertOneResult
            The inserted document.
        """
        return await self.collection.insert_one(document, **kwargs)

    async def insert_many(self, documents: Iterable, *, ordered=True, **kwargs) -> InsertManyResult:
        """Inserts many documents into the collection at once.

        Parameters
        ----------
        documents : Iterable
            The documents to upload
        ordered : Optional[bool], optional
            Inserts the documents on the server in the order provided if `True` (the default)
            If `False`, the documents will be inserted on the server in arbitary order, possibly
            in parallel, and all document inserts will be attempted.

        Returns
        -------
        InsertManyResult
            An instance of `pymongo.results.InsertManyResult`.
        """
        return await self.collection.insert_many(documents, ordered=ordered, **kwargs)

    async def bulk_write(self, requests:List, *, ordered=True, **kwargs) -> BulkWriteResult:
        """Sends a batch operations to the server.

        Parameters
        ----------
        requests : List
            A list of write operations.
        ordered : Optional[bool], optional
            If `True` (the default), the requests will be performed in the order provided. If `False`
            the documents will be inserted on the server in an arbitary order.

        Returns
        -------
        BulkWriteResult
            An instance of `pymongo.results.BulkWrite`
        """
        return await self.collection.bulk_write(requests, ordered=ordered, **kwargs)

    async def count_documents(self, filter: dict, **kwargs) -> int:
        """Counts the documents in the given collection according to the filter.

        Parameters
        ----------
        filter : dict
            The filter to use to count the documents. If an empty dictionary (`{}`) is used
            then all the documents are counted.

        Returns
        -------
        int
            The number of documents found.
        """
        return await self.collection.count_documents(filter, **kwargs)

    async def estimated_document_count(self, **kwargs) -> int:
        """Get an estimate of the number of documents in this collection using collection metadata.

        Returns
        -------
        int
            The estimated count of documents in the collection.
        """
        return await self.collection.estimated_document_count(**kwargs)

    async def find_one(self, filter: dict, *args, **kwargs) -> Optional[dict]:
        """Searches the collection for a document.

        Parameters
        ----------
        filter : dict
            A dictionary specifying the query to perform.

        Returns
        -------
        Optional[dict]
            The document if found else `None`.
        """
        return await self.collection.find_one(filter, *args, **kwargs)

    def find(self, filter: dict, *args, **kwargs) -> AsyncIOMotorCursor:
        """Generates a `motor.motor_asyncio.AsyncIOMotorCursor` object.

        Parameters
        ----------
        filter : dict
            A dictionary specifying the query to perform.

        Returns
        -------
        AsyncIOMotorCursor
            A cursor returning all the matching documents.
        """
        return self.collection.find(filter, *args, **kwargs)

    async def delete_one(self, filter: dict, **kwargs) -> DeleteResult:
        """Deletes a document from the collection mathcing the filter.

        Parameters
        ----------
        filter : dict
            A dictionary specifying the query to perform.

        Returns
        -------
        DeleteResult
            An instance of `pymongo.results.DeleteResult`
        """
        return await self.collection.delete_one(filter, **kwargs)

    async def delete_many(self, filter: dict, **kwargs) -> DeleteResult:
        """Deletes all the documents matching the filter.

        Parameters
        ----------
        filter : dict
            A dictionary specifying the query to perform.

        Returns
        -------
        DeleteResult
            An instance of `pymongo.results.DeleteResult`
        """
        return await self.collection.delete_many(filter, **kwargs)

    async def update_many(self, filter: dict, update: dict, **kwargs) -> UpdateResult:
        """Updates one or more documents that match the filter.

        Parameters
        ----------
        filter : dict
            A query that matches the documents to update.
        update : dict
            The modifications to apply.

        Returns
        -------
        UpdateResult
            An instance of `pymongo.results.UpdateResult`
        """
        return await self.collection.update_many(filter, update, **kwargs)

    async def update_one(self, filter: dict, update: dict, **kwargs) -> UpdateResult:
        """Updated a single document that matches the filter.

        Parameters
        ----------
        filter : dict
            A query that mathces the document to update.
        update : dict
            The modifications to apply.

        Returns
        -------
        UpdateResult
            An instance of `pymongo.results.UpdateResult`
        """
        return await self.collection.update_one(filter, update, **kwargs)