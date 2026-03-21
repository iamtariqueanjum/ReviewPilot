from app.core.services.github_service import GithubService


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
        ignore_files = [".git", "__pycache__", ".venv", "LICENSE", "README.md"]  # TODO make this configurable for all languages
        for item in tree_details.get('tree', []):
            if item.get('type') == 'blob' and item.get('size', 0) < 100000:  # TODO make this configurable < 100KB. Make blob a constant
                file_path = item.get('path') # app/core/services/review_service.py
                file_name = file_path.split('/')[-1]
                file_extension = file_name.split('.')[-1]
                if file_extension not in ignore_files:
                    print(f"Processing file: {file_name} with extension: {file_extension} for repo: {owner}/{repo}") # TODO replace with logger
                    for language, extensions in lang_extensions.items():
                        if file_extension in extensions:
                            # found language
                            pass
                file_sha = item.get('sha')
                file_content = self.github_service.get_blob_content(owner=owner, repo=repo, file_sha=file_sha)
                # TODO create embedding for file_content and store in vector database with metadata (owner, repo, file_path)

