"""Services that handle database connections. Implemented with MongoDB."""

from typing import Dict, Callable, Any

from motor.motor_asyncio import AsyncIOMotorCursor
from pymongo.errors import ConnectionFailure, OperationFailure, AutoReconnect
from ..helpers.logger import LOG
import asyncio
from functools import wraps
from ..conf.conf import serverTimeout


def auto_reconnect(db_func: Callable):
    """Auto reconnection decorator."""
    @wraps(db_func)
    async def retry(*args: Any, **kwargs: Any) -> Any:
        """Retry given function for many times with increasing interval.

        By default increases interval by clients default timeout for five
        times and then stops.
        :returns Async mongodb function passed to decorator
        :raises ConnectionFailure after 5 retries
        """
        interval = serverTimeout // 1000
        for wait_time in range(interval, 5 * interval, interval):
            try:
                return await db_func(*args, **kwargs)
            except AutoReconnect:
                i = int(wait_time / 10)
                if i == 5:
                    message = f"Connection to database failed after {i} tries"
                    raise ConnectionFailure(message=message)
                LOG.info("Connection not successful, trying to reconnect."
                         f"Reconnection attempt number {i}, waiting for "
                         f"{serverTimeout/1000 + wait_time} seconds")
                await asyncio.sleep(wait_time)
                continue
    return retry


class DBService:
    """Create service used for database communication.

    With this class, it is possible to create separate databases for different
    purposes (e.g. submissions and backups). Normal CRUD and some basic query
    operations are implemented.

    All services should use the same client, since Motor handles pooling
    automatically.
    """

    def __init__(self, database_name: str, db_client) -> None:
        """Create service for given database.

        Service will have read-write access to given database. Database will be
        created during first read-write operation if not already present.
        :param database_name: Name of database to be used
        """
        self.db_client = db_client
        self.database = db_client[database_name]

    @auto_reconnect
    async def create(self, collection: str, document: Dict) -> bool:
        """Insert document to collection in database.

        :param collection: Collection where document should be inserted
        :param document: Document to be inserted
        :returns: True if operation was successful
        """
        LOG.info(self.database)
        collection = self.database[collection]
        LOG.info(collection)
        result = await self.database[collection].insert_one(document)
        return result.acknowledged

    @auto_reconnect
    async def read(self, collection: str, accession_id: str) -> Dict:
        """Find object by its accessionId.

        :param collection: Collection where document should be searched from
        :param accession_id: Accession id of the document to be searched
        :returns: First document matching the accession_id
        """
        find_by_id_query = {"accessionId": accession_id}
        return await self.database[collection].find_one(find_by_id_query)

    @auto_reconnect
    async def update(self, collection: str, accession_id: str,
                     data_to_be_updated: Dict) -> bool:
        """Update some elements of object by its accessionId.

        :param collection: Collection where document should be searched from
        :param accession_id: Accession id for object to be updated
        :param data_to_be_updated: JSON representing the data that should be
        updated to object, can replace previous fields and add new ones.
        :returns: True if operation was successful
        """
        find_by_id_query = {"accessionId": accession_id}
        update_operation = {"$set": data_to_be_updated}
        result = await self.database[collection].update_one(find_by_id_query,
                                                            update_operation)
        return result.acknowledged

    @auto_reconnect
    async def replace(self, collection: str, accession_id: str,
                      new_data: Dict) -> None:
        """Replace whole object by its accessionId.

        :param collection: Collection where document should be searched from
        :param accession_id: Accession id for object to be updated
        :param new_data: JSON representing the data that replaces
        old data
        :returns: True if operation was successful
        """
        find_by_id_query = {"accessionId": accession_id}
        result = await self.database[collection].replace_one(find_by_id_query,
                                                             new_data)
        return result.acknowledged

    @auto_reconnect
    async def delete(self, collection: str, accession_id: str) -> None:
        """Delete object by its accessionId.

        :param collection: Collection where document should be searched from
        :param accession_id: Accession id for object to be updated
        :returns: True if operation was successful
        """
        find_by_id_query = {"accessionId": accession_id}
        result = await self.database[collection].delete_one(find_by_id_query)
        return result.acknowledged

    def query(self, collection: str, query: Dict) -> AsyncIOMotorCursor:
        """Query database with given query.

        Find() does no I/O and does not require an await expression, hence
        function is not async.

        :param collection: Collection where document should be searched from
        :param query: query to be used
        :returns: Async cursor instance which should be awaited when iterating
        :raises: Error when read fails for any Mongodb related reason
        """
        try:
            return self.database[collection].find(query)
        except (ConnectionFailure, OperationFailure):
            raise
