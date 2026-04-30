from langchain_core.prompts import ChatPromptTemplate
from app.integrations.llm.prompts.chatbot.system_prompt import SYSTEM_PROMPT
from app.integrations.llm.prompts.chatbot.user_prompt import USER_PROMPT


prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", USER_PROMPT)
])