import uuid


from qdrant_client.models import PointStruct

from app.core.utils.constants import VectorStore
from app.integrations.vectorstore.dao import VectorStoreDao


class VectorStoreService:

    def __init__(self):
        self.dao = VectorStoreDao()

    @staticmethod
    def chunk_to_point(chunk):
        return {
            "id": str(uuid.uuid4()),
            "vector": chunk["embedding"],
            "payload": {
                "repo": chunk["repo"],
                "owner": chunk["owner"],
                "file_path": chunk["file_path"],
                "file_name": chunk["file_name"],
                "language": chunk["language"],
                "chunk_name": chunk.get("chunk_name"),
                "chunk_index": chunk["chunk_index"],
                "start_line": chunk["chunk_start_line"],
                "end_line": chunk["chunk_end_line"],
                "commit_sha": chunk["commit_sha"],
                "created_at": chunk['created_at'],
                "updated_at": chunk['updated_at']
            }
        }

    def upsert_chunks(self, chunks):
        points = [
            PointStruct(**self.chunk_to_point(chunk))
            for chunk in chunks
        ]
        try:
            response = self.dao.client.upsert(
                collection_name=VectorStore.COLLECTION_NAME.value,
                points=points
            )
        except Exception as e:
            # TODO logger
            return None
        return response
