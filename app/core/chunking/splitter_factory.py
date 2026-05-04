from app.core.utils.constants import Language
from app.core.chunking.splitters.python_splitter import PythonSplitter
from app.core.logger import logger


class SplitterFactory:

    def __init__(self):
        self.__registry = {
            Language.PYTHON.value: PythonSplitter()
        }

    def get_splitter(self, language):
        splitter = self.__registry.get(language)
        if splitter is None:
            logger.error("Unsupported language: %s", language)
            raise ValueError(f"Unsupported Langauge: {language}")
        return splitter
