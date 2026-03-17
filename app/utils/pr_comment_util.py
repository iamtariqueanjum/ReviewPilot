def get_markdown_review_comment(response):
    issues = response.get("issues", [])
    if not issues:
        markdown_review_comment = """
        <table>
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">
                <strong>No issues found! Great job! 🎉</strong>
                </td>
            </tr>
        </table>
        """
        return markdown_review_comment
    markdown_review_comment = """
    <table>
    <tr>
        <th style="padding: 10px; border: 1px solid #ddd;">File</th>
        <th style="padding: 10px; border: 1px solid #ddd;">Line</th>
        <th style="padding: 10px; border: 1px solid #ddd;">Issue Type</th>
        <th style="padding: 10px; border: 1px solid #ddd;">Issue Description</th>
        <th style="padding: 10px; border: 1px solid #ddd;">Suggestion</th>
    </tr>
    """
    for issue in issues:
        markdown_review_comment += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">{issue.get("file", "N/A")}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{issue.get("line", "N/A")}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{issue.get("issue_type", "N/A")}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{issue.get("issue_description", "N/A")}</td>
            <td style="padding: 10px; border: 1px solid #ddd;">{issue.get("suggestion", "N/A")}</td>
        </tr>
        """
    markdown_review_comment += "</table>"
    return markdown_review_comment