

class PushEventHandler(object):

    def handle(self, payload):
        branch = payload.get("ref").replace("refs/heads/", "")
        default_branch = payload.get("repository", {}).get("default_branch")

        if branch == default_branch:
            # TODO update repo embeddings with the new changes from the push
            print(f"Push Event received on default branch... Updating latest repo embeddings....\n")
            # embedding_service.update_repo_embeddings(owner, repo)

