from app.core.celery_app import celery_app
from app.core.services.chatbot_service import ChatbotService

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.chatbot_worker.process_chat_message")
def process_chat_message(self, installation_id, owner, repo, pr_number, sender, query):
    print(f"[WORKER] Answering user query") # TODO replace with logger
    chatbot_service = ChatbotService(owner, repo, installation_id)
    response = chatbot_service.process_query(pr_number, sender, query)
    print(f"[WORKER] Answered user query") # TODO replace with logger
    return response
