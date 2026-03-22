from qdrant_client import QdrantClient


class QdrantClientWrapper:
    def __init__(self, host="localhost", port=6333): # TODO fetch from config
        self.client = QdrantClient(host=host, port=port)

    def get_client(self):
        return self.client