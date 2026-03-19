from fastapi import APIRouter, Request, status

from app.core.api.models.review_request import ReviewRequest
from app.core.utils.constants import APIEndpoints
from app.core.utils.security_util import verify_github_webhook
from app.core.services.review_service import ReviewService
from app.webhook.event_dispatcher import WebhookEventDispatcher

router = APIRouter()


@router.post(APIEndpoints.REVIEW_PR, tags=["review"], status_code=status.HTTP_204_NO_CONTENT)
async def review(request: ReviewRequest):

    print(f"Received review event\n")
    print(f"Body: {request}\n")
    # TODO handle re review requests by checking if "re_review" is True in the request
    # TODO move to ASYNC flow
    ReviewService(installation_id=request.installation_id).review_pr(
        owner=request.owner, repo=request.repo, pr_number=request.pr_number, head_sha=request.head_sha
    )
    review_id = "12345" # TODO generate a unique review ID for the review request

    return {"review_id": review_id, "message": "Review triggered successfully", "status": "queued"}


@router.post(APIEndpoints.GITHUB_WEBHOOK, tags=["webhook"], status_code=status.HTTP_204_NO_CONTENT)
async def github_webhook(request: Request):
    body = await request.body()
    payload = await request.json()

    signature = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event")
    print(f"Received GitHub webhook event: {event}\n")
    print(f"Payload: {payload}\n")
    print(f"Body: {body}\n")

    if not verify_github_webhook(body, signature):
        return {"error": "Invalid webhook signature", "status": "error"}

    WebhookEventDispatcher().dispatch(event, payload)

    return {"message": "Webhook processed successfully", "status": "success"}