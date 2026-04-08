USER_PROMPT = """
Review the following pull request. 

pull request diff:
{pr_diff}

Relevant Code Context:
{context}

Instructions:
- Compare the changes with existing implementations in the context to identify:
  - Logical inconsistencies
  - Missed reuse of existing functions/utilities
  - Deviations from established patterns
- Treat "high-impact issues" as bugs, incorrect logic, crashes, security risks, or clear maintainability problems.
- Ignore minor style issues, TODO comments, or speculative suggestions.

Now provide a detailed review.

 
"""