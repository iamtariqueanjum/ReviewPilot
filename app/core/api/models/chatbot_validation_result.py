from pydantic import BaseModel
from typing import Optional


class ValidationResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None