from langchain_core.prompts import ChatPromptTemplate
from app.prompts.review_pr.system_prompt import SYSTEM_PROMPT
from app.prompts.review_pr.user_prompt import USER_PROMPT


prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", USER_PROMPT)
])