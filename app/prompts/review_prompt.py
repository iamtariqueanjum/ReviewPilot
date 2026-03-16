from langchain_core.prompts import ChatPromptTemplate


review_prompt = ChatPromptTemplate.from_template(
"""
You are a code reviewer reviewing a pull request.

Code Diff:
{diff}

Provide feedback on:
- Bugs
- Security issues
- Performance concerns
- Code quality
"""
)