from qdrant_client import QdrantClient


class QdrantClientWrapper:
    def __init__(self, host="localhost", port=6333):
        self.host = host # TODO fetch from config
        self.port = port # TODO fetch from config
        self.client = QdrantClient(host=self.host, port=self.port)

    def get_client(self):
        return self.client