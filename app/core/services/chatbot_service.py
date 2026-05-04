import hashlib

from app.core.logger import logger
from app.core.services.embedding_service import EmbeddingService
from app.core.services.github_service import GithubService
from app.integrations.llm.llm_factory import LLMFactory
from app.integrations.llm.chains import get_chat_runnable
from app.integrations.llm.prompts.chatbot.system_prompt import SYSTEM_PROMPT
from app.integrations.llm.prompts.chatbot.user_prompt import USER_PROMPT


class ChatbotService:

    def __init__(self, owner, repo, pr_number, **kwargs):
        self.owner = owner
        self.repo = repo
        self.pr_number = pr_number
        self.github_service = GithubService(self.owner, self.repo, kwargs.get('installation_id'))
        self.embedding_service = EmbeddingService(self.owner, self.repo, kwargs.get('installation_id'))
        self.conversation_id = hashlib.sha256(
            f"{self.repo}:pr:{self.pr_number}".encode()
        ).hexdigest()[:16]
        self.llm = get_chat_runnable(LLMFactory.get_llm(kwargs.get('provider')))


    def process_query(self, sender, query):
        # TODO enhancement - Fetch pr_diff and context only if needed
        pr_details = self.github_service.get_pr(self.pr_number)
        pr_diff = self.github_service.get_pr_diff(self.pr_number, pr_details.get("head", {}).get("sha"))
        pr_filepaths = self.github_service.get_pr_filepaths(self.pr_number)
        context = self.embedding_service.get_relevant_context(pr_filepaths)
        logger.info("Retrieved context for pr %s/%s/%s", self.owner, self.repo, self.pr_number)
        # TODO exception handling
        llm_response = self.llm.invoke(
            {"input": USER_PROMPT.format(pr_diff=pr_diff, context=context, query=query), "system_prompt": SYSTEM_PROMPT},
            config={"configurable": {"session_id": self.conversation_id}}
        )
        response  = f"""@{sender} {llm_response.content}"""
        logger.info("Generated llm query response for pr %s/%s/%s", self.owner, self.repo, self.pr_number)
        self.github_service.post_comment(self.pr_number, response)
        return {"message": "Query answer comment posted successfully", "status": "success"}
