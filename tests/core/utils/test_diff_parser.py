"""Unit tests for diff_parser utilities."""

from app.core.utils.diff_parser import (
    get_new_file_line_number,
    parse_new_lines,
    prepare_changed_lines_text,
)


def test_parse_new_lines_extracts_added_lines():
    patch = """@@ -0,0 +1,3 @@
+first added
+second added
"""
    changes = parse_new_lines(patch)
    lines = [c["line"] for c in changes]
    assert lines == [1, 2]
    assert changes[0]["content"] == "first added"
    assert changes[1]["content"] == "second added"


def test_parse_new_lines_skips_blank_and_file_headers():
    patch = """diff --git a/x.py b/x.py
--- a/x.py
+++ b/x.py
@@ -10,3 +10,4 @@

 context
+only this added
"""
    changes = parse_new_lines(patch)
    assert len(changes) == 1
    assert changes[0]["content"] == "only this added"


def test_prepare_changed_lines_text():
    text = prepare_changed_lines_text(
        [{"line": 5, "content": "hello"}, {"line": 6, "content": "world"}]
    )
    assert text == "5: hello\n6: world\n"


def test_get_new_file_line_number_finds_match_forward():
    lines = ["a", "b", "target", "d"]
    assert get_new_file_line_number(lines, "target", 1) == 3


def test_get_new_file_line_number_searches_backward_when_not_ahead():
    lines = ["alpha", "beta", "gamma"]
    assert get_new_file_line_number(lines, "alpha", 3) == 1


def test_get_new_file_line_number_returns_clamped_approx_when_missing():
    lines = ["only"]
    assert get_new_file_line_number(lines, "nope", 1) == 1
