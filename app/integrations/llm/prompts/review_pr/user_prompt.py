USER_PROMPT = """
Review the following pull request. 

pull request diff:
{pr_diff}

Relevant Code Context (from repository) :
{context}

Instructions:
- Use the "Relevant Code Context" to understand how similar logic is implemented across the codebase.
- Compare the changes with existing implementations and highlight:
  - Inconsistencies in logic, structure or patterns
  - Missed reuse opportunities (existing utilities, helpers, services)
- Only report issues that are:
  - Concrete and actionable
  - Likely to cause bugs, failures or maintainability issues
- Avoid low-signal feedback such as:
  - Generic suggestions
  - Vague TODO/comment-related observations unless critical
- Prefer pointing out: 
  - What is wrong
  - Why it is wrong (based on context)
  - How it should align with existing code
- Pay special attention to:
  - Reused utilities or helper functions
  - Existing error handling patterns
  - Security-sensitive logic (auth, tokens, DB access)
- If context is not relevant, ignore it.

Now provide a detailed review.

 
"""