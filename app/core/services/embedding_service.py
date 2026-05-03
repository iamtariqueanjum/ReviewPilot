from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI

from app.core.logger import logger
from app.core.services.github_service import GithubService
from app.core.chunking.splitter_factory import SplitterFactory
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.vectorstore.service import VectorStoreService


class EmbeddingService:

    def __init__(self, owner, repo, installation_id):
        self.owner = owner
        self.repo = repo
        self.installation_id = installation_id
        self.github_service = GithubService(self.owner, self.repo, installation_id)
        self.vectorstore_service = VectorStoreService()

    def create_repo_embeddings(self):
        repo_details = self.github_service.get_repository()
        default_branch = repo_details.get('default_branch', 'main')
        branch_details = self.github_service.get_branch(branch=default_branch)
        commit_sha = branch_details.get('commit', {}).get('sha')
        if not commit_sha:
            raise ValueError(f"Could not find commit SHA for {self.owner}/{self.repo} default branch {default_branch}")
        tree_details = self.github_service.get_tree_recursive(tree_sha=commit_sha)
        lang_extensions = { # TODO make this configurable
            "Python": ["py"],
            "Java": ["java"]
        }
        # TODO make this configurable for all languages
        ignore_files = [".git", "__pycache__", ".venv", "LICENSE", "md"]
        for item in tree_details.get('tree', []):
            # TODO make this configurable < 100KB. Make blob a constant
            if item.get('type') == 'blob' and item.get('size', 0) < 100000:
                file_path = item.get('path')
                file_name = file_path.split('/')[-1]
                file_extension = file_name.split('.')[-1]
                file_sha = item.get('sha')
                file_content = self.github_service.get_blob_content(file_sha=file_sha)
                if file_extension not in ignore_files:
                    logger.info("[WORKER] Processing file %s with extension: %s for repo: %s/%s",
                                file_path, file_extension, self.owner, self.repo)
                    for language, extensions in lang_extensions.items():
                        if file_extension in extensions:
                            splitter = SplitterFactory().get_splitter(language=language)
                            payload = {'owner': self.owner, 'repo': self.repo, 'file_name': file_name,
                                       'file_extension': file_extension, 'language': language,
                                       'file_content': file_content, 'file_path': file_path, 'commit_sha': commit_sha}
                            chunks = splitter.split(payload)
                            if not chunks:
                                continue
                            # chunks = self.generate_code_summaries(chunks) # TODO move this to async flow after insert
                            chunks = self.generate_embeddings(chunks)
                            self.vectorstore_service.upsert_chunks(chunks)


    # TODO FIX THIS - summaries not saved in vector db
    @staticmethod
    def generate_code_summaries(chunks):
        llm = LLMFactory.get_llm(provider="openai") # TODO make provider configurable
        for chunk in chunks:
            code = chunk.get('chunk_content')
            prompt = "Summarize the code in a single line code: {code}"
            prompt_template = ChatPromptTemplate.from_template(prompt)
            chain = prompt_template | llm
            try:
                result = chain.invoke({"code": code}) # TODO Batch processing optimisation
                chunk['summary'] = result.content
            except Exception as e:
                logger.error("[WORKER] Failed to generate code summary for chunk %s: %s", chunk.get('chunk_id'), str(e))
                chunk['summary'] = "Summary not available"
                # TODO add retry mechanism and Handle Partial Failures
        return chunks


    @staticmethod
    def call_openai_embeddings(content):
        client = OpenAI()
        try:
            response = client.embeddings.create(
                model="text-embedding-3-large",  # TODO fetch from ConfigConstants
                input=content
            )
        except Exception as e: # TODO exception handling
            raise e
        return response


    def generate_embeddings(self, chunks):
        for chunk in chunks:
            response = self.call_openai_embeddings(chunk['chunk_content'])  # TODO optimisation batch embeddings
            chunk['embedding'] = response.data[0].embedding
            chunk['created_at'] = datetime.utcnow()
            chunk['updated_at'] = datetime.utcnow()
        return chunks

    def get_relevant_context(self, file_paths):
        filtered_chunks = []
        for file_path in file_paths:
            filtered_chunks.append(self.vectorstore_service.filter_chunks_by_filepath(self.repo, file_path))
        # TODO enhancement: add semantic search of files
        context = ""
        for filtered_chunk in filtered_chunks:
            chunks, _ = filtered_chunk
            chunks = sorted(chunks, key=lambda x: x.dict()["payload"]["chunk_index"])

            for chunk in chunks:
                payload = chunk.dict().get('payload', {})
                context += f"File Path: {payload['file_path']}\n"
                context += f"Function: {payload['chunk_name']}\n"
                context += f"Code: \n{payload['chunk_content']}\n\n\n"
                # TODO add summary

        return context
