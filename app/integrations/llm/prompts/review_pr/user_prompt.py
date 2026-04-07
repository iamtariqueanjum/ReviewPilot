USER_PROMPT = """
Review the following pull request. 

pull request diff:
{pr_diff}

Relevant Code Context (from repository) :
{context}

Instructions:
- Use the "Relevant Code Context" to understand how similar logic is implemented elsewhere in the codebase.
- Identify inconsistencies between the new changes and existing patterns.
- Pay special attention to:
  - Reused utilities or helper functions
  - Existing error handling patterns
  - Security-sensitive logic (auth, tokens, DB access)
- Do NOT repeat issues already handled correctly in context.
- If context is not relevant, ignore it.

Now provide a detailed review.

 
"""