from qdrant_client.models import VectorParams, Distance

from app.core.utils.constants import VectorStore
from app.integrations.vectorstore.client import QdrantClientWrapper


class VectorStoreDao:

    def __init__(self):
        self.client = QdrantClientWrapper().get_client()
        self.collection = VectorStore.COLLECTION_NAME.value
        self.vector_size = VectorStore.VECTOR_SIZE.value

    def create_collection(self):
        print(f"CREATING COLLECTION: {self.collection}")
        try:
            response = self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=int(self.vector_size),
                    distance=Distance.COSINE
                ))
        except Exception as e:
            # TODO loggger
            return None
        return response

    def delete_collection(self):
        print(f"DELETING COLLECTION: {self.collection}")
        try:
            response = self.client.delete_collection(collection_name=self.collection)
        except Exception as e:
            # TODO loggger
            return None
        return response
