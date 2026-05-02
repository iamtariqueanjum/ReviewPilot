from pydantic import BaseModel


class ChatbotResponse(BaseModel):
    response: str
