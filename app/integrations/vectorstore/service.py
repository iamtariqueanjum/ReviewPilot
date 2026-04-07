import uuid


from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue

from app.core.utils.constants import VectorStore
from app.integrations.vectorstore.dao import VectorStoreDao


class VectorStoreService:

    def __init__(self):
        self.dao = VectorStoreDao()
        self.dao.create_collection()  # TODO move to app startup script

    @staticmethod
    def chunk_to_point(chunk):
        print(f"Chunk to Point: file_path-{chunk["file_path"]}-chunk_id-{chunk["chunk_id"]}")
        return {
            "id": str(uuid.uuid4()),
            "vector": chunk["embedding"],
            "payload": {
                "owner": chunk["owner"],
                "repo": chunk["repo"],
                "file_path": chunk["file_path"],
                "file_name": chunk["file_name"],
                "file_extension": chunk["file_extension"],
                "language": chunk["language"],
                "chunk_id": chunk["chunk_id"],
                "chunk_name": chunk["chunk_name"],
                "chunk_content": chunk["chunk_content"], # TODO move to DB store from vector store
                "chunk_index": chunk["chunk_index"],
                "start_line": chunk["chunk_start_line"],
                "end_line": chunk["chunk_end_line"],
                "imports": chunk["imports"],
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
        print(f"UPSERTING CHUNKS: {points}")
        try:
            response = self.dao.client.upsert(
                collection_name=VectorStore.COLLECTION_NAME.value,
                points=points
            )
        except Exception as e:
            # TODO logger
            return None
        return response


    def filter_chunks_by_filepath(self, repo, file_path, limit=50):
        results = self.dao.client.scroll(
            collection_name=VectorStore.COLLECTION_NAME.value,
            scroll_filter=Filter(
                    must=[
                        FieldCondition(key="repo", match=MatchValue(value=repo)),
                        FieldCondition(key="file_path", match=MatchValue(value=file_path))
                    ]
                ),
                limit=limit
            )
        return results