from langchain_core.prompts import ChatPromptTemplate
from system_prompt import SYSTEM_PROMPT


prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Review the following pull request diff.\n\n{pr_diff}")
])
