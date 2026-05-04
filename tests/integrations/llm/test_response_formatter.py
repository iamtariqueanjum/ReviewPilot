"""Unit tests for LLM response formatting."""

from types import SimpleNamespace

from app.integrations.llm.response_formatter import get_markdown_review_comment


def test_get_markdown_review_comment_no_issues():
    text = get_markdown_review_comment(SimpleNamespace(issues=[]))
    assert "No issues found" in text


def test_get_markdown_review_comment_builds_table():
    issues = [
        SimpleNamespace(
            file="app/x.py",
            line=10,
            issue_type="bug",
            issue_description="off-by-one",
            suggestion="use range(len)-1",
        )
    ]
    md = get_markdown_review_comment(SimpleNamespace(issues=issues))
    assert "app/x.py" in md
    assert "10" in md
    assert "off-by-one" in md
    assert "File" in md and "Suggestion" in md
