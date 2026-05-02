from app.core.api.models.chatbot_response import ChatbotResponse
from app.core.services.github_service import GithubService
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.llm.prompts.chatbot.final_prompt import prompt


class ChatbotService:

    def __init__(self, owner, repo, installation_id, provider=None):
        self.owner = owner
        self.repo = repo
        self.github_service = GithubService(self.owner, self.repo, installation_id)
        self.llm = LLMFactory.get_llm(provider)
        self.structured_llm = self.llm.with_structured_output(ChatbotResponse)
        self.chain = prompt | self.structured_llm


    def process_query(self, pr_number, sender, query):
        # TODO exception handling
        llm_response = self.chain.invoke({"query": query})
        response = getattr(llm_response, "response", "Sorry, I couldn't generate a response.")
        response  = f"""@{sender} {response}"""
        self.github_service.post_comment(pr_number, response)