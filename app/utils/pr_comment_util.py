from tabulate import tabulate

def get_markdown_review_comment(response):
    issues = getattr(response, "issues", [])

    if not issues:
        markdown_review_comment = "No issues found! Great job! 🎉"
        return markdown_review_comment
    table = []
    for issue in issues:
        table.append([
            getattr(issue, "file", "N/A"),
            getattr(issue, "line", "N/A"),
            getattr(issue, "issue_type", "N/A"),
            getattr(issue, "issue_description", "N/A"),
            getattr(issue, "suggestion", "N/A")
        ])
    return tabulate(table, headers=["File", "Line", "Type", "Issue", "Suggestion"], tablefmt="github")