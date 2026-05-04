from fastapi import APIRouter, Request, status

from app.core.logger import logger
from app.core.utils.constants import APIEndpoints
from app.core.utils.security_util import verify_github_webhook
from app.webhook.event_dispatcher import WebhookEventDispatcher

router = APIRouter()

@router.post(APIEndpoints.GITHUB_WEBHOOK, tags=["webhook"], status_code=status.HTTP_204_NO_CONTENT)
async def github_webhook(request: Request):
    body = await request.body()
    payload = await request.json()
    event = request.headers.get("x-github-event")
    signature = request.headers.get("x-hub-signature-256")

    logger.info("Received webhook event: %s Body: %s", event, body)

    if not verify_github_webhook(body, signature):
        return {"error": "Invalid webhook signature", "status": "error"}

    WebhookEventDispatcher().dispatch(event, payload)

    return {"message": "Webhook processed successfully", "status": "success"}
