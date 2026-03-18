from pydantic import BaseModel


class ReviewRequest(BaseModel):
    owner: str
    repo: str
    pr_number: int
    head_sha: str
    installation_id: int
    re_review: bool = False