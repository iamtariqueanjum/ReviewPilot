from enum import Enum


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"