from app.core.api.models.review_response import ReviewLLMResponse
from app.core.services.embedding_service import EmbeddingService
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.llm.prompts.review_pr.final_prompt import prompt
from app.integrations.llm.response_formatter import get_markdown_review_comment
from app.core.services.github_service import GithubService


class ReviewService(object):

    def __init__(self, owner, repo, installation_id, provider=None):
        self.owner = owner
        self.repo = repo
        self.installation_id = installation_id
        self.github_service = GithubService(self.owner, self.repo, installation_id)
        self.embedding_service = EmbeddingService(self.owner, self.repo, installation_id)
        self.llm = LLMFactory.get_llm(provider)
        self.structured_llm = self.llm.with_structured_output(ReviewLLMResponse)
        self.chain = prompt | self.structured_llm

    def review_pr(self, pr_number, head_sha):
        pr_diff = self.github_service.get_pr_diff(pr_number, head_sha)
        print(f"PR Diff for {self.owner}/{self.repo}#{pr_number}:\n{pr_diff}\n")
        pr_filepaths = self.github_service.get_pr_filepaths(pr_number)
        context = self.embedding_service.get_relevant_context(pr_filepaths)
        # TODO exception handling
        llm_response = self.chain.invoke(
            {"pr_diff": pr_diff, "context": context}
        )
        print(f"LLM response for PR review:\n{llm_response}\n")
        body = get_markdown_review_comment(llm_response)
        print(f"Generated review comment for {self.owner}/{self.repo}#{pr_number}:\n{body}\n")
        self.github_service.post_comment(pr_number, body)
        return {"message": "Review comment posted successfully", "status": "success"}
