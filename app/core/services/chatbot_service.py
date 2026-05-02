from app.core.api.models.chatbot_response import ChatbotResponse
from app.core.services.embedding_service import EmbeddingService
from app.core.services.github_service import GithubService
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.llm.prompts.chatbot.final_prompt import prompt


class ChatbotService:

    def __init__(self, owner, repo, installation_id, provider=None):
        self.owner = owner
        self.repo = repo
        self.github_service = GithubService(self.owner, self.repo, installation_id)
        self.embedding_service = EmbeddingService(self.owner, self.repo, installation_id)
        self.llm = LLMFactory.get_llm(provider)
        self.structured_llm = self.llm.with_structured_output(ChatbotResponse)
        self.chain = prompt | self.structured_llm


    def process_query(self, pr_number, sender, query):
        pr_details = self.github_service.get_pr(pr_number)
        pr_diff = self.github_service.get_pr_diff(pr_number, pr_details.get("head", {}).get("sha"))
        pr_filepaths = self.github_service.get_pr_filepaths(pr_number)
        context = self.embedding_service.get_relevant_context(pr_filepaths)
        # TODO exception handling
        llm_response = self.chain.invoke(
            {"pr_diff": pr_diff, "context": context, "query": query}
        )
        response = getattr(llm_response, "response", "Sorry, I couldn't generate a response.")
        response  = f"""@{sender} {response}"""
        self.github_service.post_comment(pr_number, response)
        return {"message": "Query answer comment posted successfully", "status": "success"}