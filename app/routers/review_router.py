import logging

from fastapi import APIRouter, status

from app.models.review_request import ReviewRequest
from app.utils.constants import APIEndpoints


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(APIEndpoints.REVIEW_PR, tags=["review"], status_code=status.HTTP_204_NO_CONTENT)
async def review(request: ReviewRequest):
    body = await request.body()
    payload = await request.json()

    print(f"Received review event\n")
    print(f"Payload: {payload}\n")
    print(f"Body: {body}\n")
    # review_service.review_pr(
    #     owner=request.owner,
    #     repo=request.repo,
    #     pr_number=request.pr_number
    # )
    review_id = "12345" # TODO generate a unique review ID for the review request

    return {"review_id": review_id, "message": "Review triggered successfully", "status": "queued"}