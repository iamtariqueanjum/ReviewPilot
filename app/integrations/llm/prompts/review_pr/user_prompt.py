USER_PROMPT = """
Review the following pull request. 

pull request diff:
{pr_diff}

Relevant Code Context (from repository) :
{context}

Instructions:
- Compare the changes with existing code and identify inconsistencies, bugs, or missed reuse opportunities.
- Focus only on concrete, high-impact issues.
- Avoid generic or low-signal feedback.
- If context is not relevant, ignore it.

Now provide a detailed review.

 
"""