from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.models.review_response import ReviewLLMResponse
from app.prompts.review_pr.system_prompt import SYSTEM_PROMPT
from app.prompts.review_pr.user_prompt import USER_PROMPT


parser = PydanticOutputParser(pydantic_object=ReviewLLMResponse)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", USER_PROMPT)
]).partial(format_instructions=parser.get_format_instructions())
