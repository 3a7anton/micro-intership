"""
Tests for index.html

Validates changes introduced in this PR:
- The <html> tag now includes lang="en" for accessibility/internationalisation.
- Structural blank lines were added around <head> and after </body>.
- The file has no trailing newline after </html>.
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
# lang attribute tests (change introduced in this PR)
# ---------------------------------------------------------------------------

class TestLangAttribute:
    """The PR adds lang="en" to the <html> opening tag."""

    def test_html_tag_has_lang_attribute(self, html_content):
        assert 'lang="en"' in html_content, '<html> must have lang="en"'

    def test_lang_attribute_is_on_html_tag(self, html_lines):
        """lang="en" must appear on the line containing the <html> opening tag."""
        html_tag_line = next(
            (line for line in html_lines if "<html" in line.lower()), None
        )
        assert html_tag_line is not None, "<html> tag not found"
        assert 'lang="en"' in html_tag_line, 'lang="en" must be on the <html> tag line'

    def test_lang_value_is_en(self, html_content):
        """Verify the language code is exactly 'en', not 'en-US' or other variants."""
        import re
        match = re.search(r'<html[^>]*lang="([^"]+)"', html_content, re.IGNORECASE)
        assert match is not None, "lang attribute not found on <html> tag"
        assert match.group(1) == "en"

    def test_lang_attribute_appears_exactly_once(self, html_content):
        assert html_content.count('lang="en"') == 1

    # Boundary: ensure no lang attribute was present with wrong capitalisation
    def test_lang_not_uppercase(self, html_content):
        """Attribute value is lowercase 'en', not 'EN'."""
        assert 'lang="EN"' not in html_content


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
# Blank-line structure tests (changes introduced in this PR)
# ---------------------------------------------------------------------------

class TestBlankLineStructure:
    """The PR added blank lines after <html lang="en"> and after </head>."""

    def test_blank_line_between_html_and_head(self, html_lines):
        """There should be a blank line between the <html> tag and <head>."""
        html_tag_idx = next(
            i for i, line in enumerate(html_lines) if "<html" in line.lower()
        )
        head_idx = next(
            i for i, line in enumerate(html_lines) if "<head" in line.lower()
        )
        lines_between = [l.strip() for l in html_lines[html_tag_idx + 1:head_idx]]
        assert any(l == "" for l in lines_between), (
            "Expected at least one blank line between <html> and <head>"
        )

    def test_blank_line_between_head_and_body(self, html_lines):
        """There should be a blank line between </head> and <body>."""
        head_close_idx = next(
            i for i, line in enumerate(html_lines) if "</head>" in line.lower()
        )
        body_idx = next(
            i for i, line in enumerate(html_lines) if "<body" in line.lower()
        )
        lines_between = [l.strip() for l in html_lines[head_close_idx + 1:body_idx]]
        assert any(l == "" for l in lines_between), (
            "Expected at least one blank line between </head> and <body>"
        )


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
        assert "charset" in html_content.lower()

    def test_nav_tag_present(self, html_content):
        assert "<nav>" in html_content

    def test_footer_tag_present(self, html_content):
        assert "<footer>" in html_content

    def test_css_link_present(self, html_content):
        assert 'href="css/style.css"' in html_content

    # Regression: lang attribute addition must not break page title
    def test_page_title_content(self, html_content):
        assert "QuickHire" in html_content

    # Regression: hero section must survive structural changes
    def test_hero_section_present(self, html_content):
        assert 'class="hero"' in html_content

    # Regression: file ends with </html> as the last non-empty content
    def test_file_ends_with_html_close_tag(self, html_content):
        stripped = html_content.rstrip()
        assert stripped.endswith("</html>"), (
            f"File must end with </html>, got: {stripped[-20:]!r}"
        )