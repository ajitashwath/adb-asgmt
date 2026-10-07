from datetime import datetime, timezone
from pymongo import DESCENDING


class TodoRepository:
    def __init__(self, db, collection_name='todos'):
        self._collection = db[collection_name]
        self._index_created = False

    def list_all(self, limit, offset=0):
        self._ensure_index()
        cursor = (self._collection.find()
                  .sort([('created_at', DESCENDING), ('_id', DESCENDING)])
                  .skip(offset)
                  .limit(limit))
        return [self._serialize(doc) for doc in cursor]

    def create(self, description):
        doc = {'description': description, 'created_at': datetime.now(timezone.utc)}
        self._collection.insert_one(doc)
        return self._serialize(doc)

    def _ensure_index(self):
        if not self._index_created:
            self._collection.create_index([('created_at', DESCENDING), ('_id', DESCENDING)])
            self._index_created = True

    @staticmethod
    def _serialize(doc):
        created_at = doc['created_at'].replace(tzinfo=timezone.utc)
        return {
            'id': str(doc['_id']),
            'description': doc['description'],
            'created_at': created_at.isoformat(),
        }
