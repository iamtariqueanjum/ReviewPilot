from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate

from app.core.services.github_service import GithubService
from app.core.chunking.splitter_factory import SplitterFactory
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.vectorstore.service import VectorStoreService


class EmbeddingService(object):

    def __init__(self, installation_id):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)


    def create_repo_embeddings(self, owner, repo):
        repo_details = self.github_service.get_repository(owner=owner, repo=repo)
        default_branch = repo_details.get('default_branch', 'main')
        branch_details = self.github_service.get_branch(owner=owner, repo=repo, branch=default_branch)
        commit_sha = branch_details.get('commit', {}).get('sha')
        if not commit_sha:
            raise ValueError(f"Could not find commit SHA for {owner}/{repo} default branch {default_branch}")
        tree_details = self.github_service.get_tree_recursive(owner=owner, repo=repo, tree_sha=commit_sha)
        lang_extensions = { # TODO make this configurable
            "Python": ["py"],
            "Java": ["java"]
        }
        ignore_files = [".git", "__pycache__", ".venv", "LICENSE", "md"]  # TODO make this configurable for all languages
        for item in tree_details.get('tree', []):
            if item.get('type') == 'blob' and item.get('size', 0) < 100000:  # TODO make this configurable < 100KB. Make blob a constant
                file_path = item.get('path') # app/core/services/review_service.py
                file_name = file_path.split('/')[-1]
                file_extension = file_name.split('.')[-1]
                file_sha = item.get('sha')
                file_content = self.github_service.get_blob_content(owner=owner, repo=repo, file_sha=file_sha)
                if file_extension not in ignore_files:
                    print(f"Processing file: {file_path} with extension: {file_extension} for repo: {owner}/{repo}") # TODO replace with logger
                    for language, extensions in lang_extensions.items():
                        print(f"Language {language}: {extensions}")
                        if file_extension in extensions:
                            splitter = SplitterFactory().get_splitter(language=language)
                            payload = {'owner': owner, 'repo': repo, 'file_name': file_name,
                                       'file_extension': file_extension, 'language': language, 'file_content': file_content,
                                       'file_path': file_path, 'commit_sha': commit_sha}
                            chunks = splitter.split(payload)
                            if not chunks:
                                continue
                            chunks = self.generate_code_summaries(chunks)
                            print(f"FUNKY Generated chunks before embeddings\n{chunks}\n")
                            chunks = self.generate_embeddings(chunks)
                            print(f"FUNKY Generated chunks after embeddings\n{chunks}\n")
                            VectorStoreService().upsert_chunks(chunks)


    @staticmethod
    def generate_code_summaries(chunks):
        llm = LLMFactory.get_llm(provider="openai") # TODO make provider configurable
        for chunk in chunks:
            code = chunk.get('chunk_content')
            prompt = f"""Summarize the code in a single line code: {code}"""
            prompt_template = ChatPromptTemplate.from_template(prompt)
            chain = prompt_template | llm
            try:
                result = chain.invoke({"code": code}) # TODO Batch processing optimisation
                chunk['summary'] = result.content
            except Exception as e:
                print(f"Error generating summary for chunk: {chunk.get('chunk_id')}, error: {str(e)}") # TODO replace with logger
                chunk['summary'] = "Summary not available"
                # TODO add retry mechanism and Handle Partial Failures
        return chunks


    @staticmethod
    def call_openai_embeddings(content):
        from openai import OpenAI
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

    @staticmethod
    def call_openai_embeddings(content):
        from openai import OpenAI
        client = OpenAI()
        try:
            response = client.embeddings.create(
                model="text-embedding-3-large",  # TODO fetch from ConfigConstants
                input=content
            )
        except Exception as e:
            raise e
        return response