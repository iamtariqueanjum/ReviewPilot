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
