from qdrant_client import QdrantClient

from app.core.utils.constants import ConfigConstants

class QdrantClientWrapper:

    def __init__(self):
        self.host = ConfigConstants.QDRANT_BACKEND_HOST
        self.port = ConfigConstants.QDRANT_BACKEND_PORT
        self.client = QdrantClient(host=self.host, port=self.port)

    def get_client(self):
        return self.client
