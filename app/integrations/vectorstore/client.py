from qdrant_client import QdrantClient

from app.core.utils.constants import ConfigConstants

class QdrantClientWrapper:

    def __init__(self):
        self.host = ConfigConstants.QDRANT_BACKEND_HOST.value
        self.port = int(ConfigConstants.QDRANT_BACKEND_PORT.value)
        self.client = QdrantClient(host=self.host, port=self.port)

    def get_client(self):
        return self.client
