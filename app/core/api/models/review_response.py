from pydantic import BaseModel
from typing import List, Optional


class ReviewIssue(BaseModel):
    file: str
    line: int
    issue_type: str
    issue_description: str
    suggestion: str
    fix: Optional[str] = None


class ReviewLLMResponse(BaseModel):
    issues: List[ReviewIssue]