from app.core.utils.constants import Language
from app.core.chunking.splitters.python_splitter import PythonSplitter


class SplitterFactory:

    def __init__(self):
        self.__registry = {
            Language.PYTHON.value: PythonSplitter
        }

    def get_splitter(self, language: str):
        splitter = self.__registry.get(language)
        if splitter is None:
            raise ValueError(f"Unsupported Langauge: {language}")