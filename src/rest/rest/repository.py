from datetime import datetime, timezone


class TodoRepository:
    """Persistence layer for todos, backed by a MongoDB collection."""

    def __init__(self, db, collection_name='todos'):
        self._collection = db[collection_name]

    def list_all(self):
        # Oldest first, so new todos appear at the bottom of the list.
        return [self._serialize(doc) for doc in self._collection.find().sort('created_at', 1)]

    def create(self, description):
        doc = {'description': description, 'created_at': datetime.now(timezone.utc)}
        self._collection.insert_one(doc)  # adds `_id` to doc
        return self._serialize(doc)

    @staticmethod
    def _serialize(doc):
        # Mongo stores UTC but pymongo returns naive datetimes by default.
        created_at = doc['created_at'].replace(tzinfo=timezone.utc)
        return {
            'id': str(doc['_id']),
            'description': doc['description'],
            'created_at': created_at.isoformat(),
        }
