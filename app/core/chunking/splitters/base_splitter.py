from abc import ABC, abstractmethod



class BaseSplitter(ABC):

    def __init__(self):
        # TODO chunk_size and overlap based sliding window as fallback
        pass

    @abstractmethod
    def split(self, owner, repo, file_name, extension, language,file_content, file_path, commit_sha):
        pass
