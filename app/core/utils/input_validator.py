import re
from app.core.api.models.chatbot_validation_result import ValidationResult


class InputValidator:
    MAX_INPUT_LENGTH = 2000

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore (previous|above|all) instructions",
        r"forget (everything|all|previous)",
        r"you are now",
        r"new instruction",
        r"system prompt",
        r"jailbreak",
        r"dan mode",
        r"developer mode",
    ]

    PII_PATTERNS = [
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # email
        r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal token
        r"github_pat_[a-zA-Z0-9_]{82}",  # GitHub fine-grained token
        r"sk-[a-zA-Z0-9]{48}",  # OpenAI key
        r"(?<!\w)\d{16}(?!\w)",  # credit card
    ]

    def validate(self, user_input: str) -> ValidationResult:
        if len(user_input) > self.MAX_INPUT_LENGTH:
            return ValidationResult(
                is_safe=False,
                reason="Input exceeds maximum allowed length"
            )
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return ValidationResult(
                    is_safe=False,
                    reason="Input contains potential prompt injection pattern"
                )
        for pattern in self.PII_PATTERNS:
            if re.search(pattern, user_input):
                return ValidationResult(
                    is_safe=False,
                    reason="Input contains potential personally identifiable information"
                )
        sanitized = self.sanitize(user_input)
        return ValidationResult(
            is_safe=True,
            sanitized_input=sanitized
        )


    @staticmethod
    def sanitize(user_input: str) -> str:
        # Remove HTML/script tags
        user_input = re.sub(r"<[^>]*>", "", user_input)
        # Normalize whitespace
        user_input = re.sub(r"\s+", " ", user_input).strip()
        return user_input
