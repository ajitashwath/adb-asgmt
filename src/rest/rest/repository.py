from datetime import datetime, timezone

from pymongo import DESCENDING


class TodoRepository:
    """Persistence layer for todos, backed by a MongoDB collection."""

    def __init__(self, db, collection_name='todos'):
        self._collection = db[collection_name]
        self._index_created = False

    def list_all(self, limit, offset=0):
        """Return a page of todos, newest first."""
        self._ensure_index()
        cursor = (self._collection.find()
                  .sort([('created_at', DESCENDING), ('_id', DESCENDING)])
                  .skip(offset)
                  .limit(limit))
        return [self._serialize(doc) for doc in cursor]

    def create(self, description):
        doc = {'description': description, 'created_at': datetime.now(timezone.utc)}
        self._collection.insert_one(doc)  # adds `_id` to doc
        return self._serialize(doc)

    def _ensure_index(self):
        # Created lazily (not in __init__) so the API can start before Mongo is reachable.
        if not self._index_created:
            self._collection.create_index([('created_at', DESCENDING), ('_id', DESCENDING)])
            self._index_created = True

    @staticmethod
    def _serialize(doc):
        # Mongo stores UTC but pymongo returns naive datetimes by default.
        created_at = doc['created_at'].replace(tzinfo=timezone.utc)
        return {
            'id': str(doc['_id']),
            'description': doc['description'],
            'created_at': created_at.isoformat(),
        }
