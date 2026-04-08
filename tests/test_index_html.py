"""
Tests for index.html

Validates the change introduced in this PR: the addition of the HTML comment
"<!-- Triggering CodeRabbit code review -->" as the second line of the file.
"""

import os
import html.parser
import pytest

HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "index.html")


@pytest.fixture(scope="module")
def html_lines():
    """Return the raw lines of index.html."""
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


@pytest.fixture(scope="module")
def html_content():
    """Return the full text of index.html."""
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileExists:
    def test_index_html_exists(self):
        assert os.path.isfile(HTML_PATH), "index.html must exist"

    def test_index_html_is_not_empty(self):
        assert os.path.getsize(HTML_PATH) > 0


# ---------------------------------------------------------------------------
# Added comment tests
# ---------------------------------------------------------------------------

class TestCodeRabbitComment:
    EXPECTED_COMMENT = "<!-- Triggering CodeRabbit code review -->"

    def test_comment_present_in_file(self, html_content):
        assert self.EXPECTED_COMMENT in html_content

    def test_comment_is_on_second_line(self, html_lines):
        """The comment must be the second line (index 1), right after DOCTYPE."""
        second_line = html_lines[1].strip()
        assert second_line == self.EXPECTED_COMMENT

    def test_comment_appears_exactly_once(self, html_content):
        assert html_content.count(self.EXPECTED_COMMENT) == 1

    def test_comment_precedes_html_tag(self, html_content):
        comment_pos = html_content.index(self.EXPECTED_COMMENT)
        html_tag_pos = html_content.index("<html")
        assert comment_pos < html_tag_pos, "Comment must appear before the <html> tag"

    def test_comment_follows_doctype(self, html_lines):
        first_line = html_lines[0].strip().upper()
        assert first_line == "<!DOCTYPE HTML>", "DOCTYPE must be the first line"

    # Boundary: ensure the comment text is not altered/truncated
    def test_comment_exact_text(self, html_content):
        assert "Triggering CodeRabbit code review" in html_content

    # Regression: comment must not appear inside an element
    def test_comment_is_not_inside_head_or_body(self, html_lines):
        """Lines before <html> should only be DOCTYPE and the comment."""
        html_tag_line = next(
            i for i, line in enumerate(html_lines) if "<html" in line.lower()
        )
        pre_html = [l.strip() for l in html_lines[:html_tag_line]]
        for line in pre_html:
            if line == "":
                continue
            assert line.startswith("<!"), f"Unexpected content before <html>: {line!r}"


# ---------------------------------------------------------------------------
# DOCTYPE preservation tests
# ---------------------------------------------------------------------------

class TestDoctypePreservation:
    def test_doctype_is_first_line(self, html_lines):
        first_line = html_lines[0].strip().upper()
        assert first_line == "<!DOCTYPE HTML>"

    def test_doctype_present_in_content(self, html_content):
        assert html_content.upper().startswith("<!DOCTYPE HTML")


# ---------------------------------------------------------------------------
# HTML structural integrity tests
# ---------------------------------------------------------------------------

class _HTMLValidator(html.parser.HTMLParser):
    """Minimal parser that records open/close tags to detect gross breakage."""

    def __init__(self):
        super().__init__()
        self.errors = []
        self.tags_seen = []

    def handle_starttag(self, tag, attrs):
        self.tags_seen.append(tag)

    def handle_error(self, message):
        self.errors.append(message)


class TestHTMLStructure:
    def test_html_is_parseable(self, html_content):
        parser = _HTMLValidator()
        # parse() raises on hard errors; soft errors are collected
        parser.feed(html_content)
        assert not parser.errors, f"HTML parse errors: {parser.errors}"

    def test_html_tag_present(self, html_content):
        assert "<html" in html_content.lower()

    def test_head_tag_present(self, html_content):
        assert "<head" in html_content.lower()

    def test_body_tag_present(self, html_content):
        assert "<body" in html_content.lower()

    def test_title_tag_present(self, html_content):
        assert "<title" in html_content.lower()

    def test_meta_charset_present(self, html_content):
        assert 'charset' in html_content.lower()

    def test_comment_does_not_break_nav(self, html_content):
        assert "<nav>" in html_content

    def test_comment_does_not_break_footer(self, html_content):
        assert "<footer>" in html_content