from typing import Optional
from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_safe: bool
    reason: Optional[str] = None
    sanitized_input: Optional[str] = None
