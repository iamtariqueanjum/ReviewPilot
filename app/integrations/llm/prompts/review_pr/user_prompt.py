USER_PROMPT = """
Review the following pull request. 

pull request diff:
{pr_diff}

Relevant Code Context:
{context}

Instructions:
- Compare the diff changes with existing implementations in the context to identify:
  - Logical inconsistencies
  - Missed reuse of existing functions/utilities
  - Deviations from established patterns
- Treat "high-impact issues" as bugs, incorrect logic, crashes, security risks, or clear maintainability problems.
- Ignore minor style issues, TODO comments, or speculative suggestions.
- The pull request diff is the only source of truth for generating issues.
- Context is provided only for comparison and must not be reviewed independently.
- Never generate feedback about code that is not part of the diff.
- If no issues are found in the diff, return no issues found.

Now provide a detailed review.

 
"""