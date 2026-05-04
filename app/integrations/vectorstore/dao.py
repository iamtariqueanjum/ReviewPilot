from qdrant_client.models import VectorParams, Distance

from app.core.utils.constants import VectorStore
from app.integrations.logger import logger
from app.integrations.vectorstore.client import QdrantClientWrapper


class VectorStoreDao:

    def __init__(self):
        self.client = QdrantClientWrapper().get_client()
        self.collection = VectorStore.COLLECTION_NAME.value
        self.vector_size = VectorStore.VECTOR_SIZE.value

    def create_collection(self):
        try:
            response = self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=int(self.vector_size),
                    distance=Distance.COSINE
                ))
            logger.info("Created collection %s with vector size %s: %s", self.collection, self.vector_size, response)
        except Exception as e:
            logger.exception("Error while creating collection %s: %s", self.collection, str(e))
            return None
        return response

    def delete_collection(self):
        try:
            response = self.client.delete_collection(collection_name=self.collection)
            logger.info("Deleted Collection %s: %s", self.collection, response)
        except Exception as e:
            logger.exception("Error while deleting collection %s: %s", self.collection, str(e))
            return None
        return response
