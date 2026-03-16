from pydantic import BaseModel


class ReviewRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    installation_id: int
    re_review: bool = False