from app.core.services.github_service import GithubService


class EmbeddingService(object):

    def __init__(self, installation_id):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)


    def create_repo_embeddings(self, owner, repo):
        repo_details = self.github_service.get_repository(owner=owner, repo=repo)
        default_branch = repo_details.get('default_branch', 'main')
