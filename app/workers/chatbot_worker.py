from app.core.celery_app import celery_app
from app.core.services.chatbot_service import ChatbotService
from app.workers.logger import logger


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.chatbot_worker.process_chat_message")
def process_chat_message(self, installation_id, owner, repo, pr_number, sender, query):
    logger.info("Answering user query %s %s", sender, query)
    chatbot_service = ChatbotService(owner, repo, pr_number, installation_id=installation_id)
    response = chatbot_service.process_query(sender, query)
    logger.info("Answered user query sender- %s query- %s\n Response- %s", sender, query, response)
    return response
