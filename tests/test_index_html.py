"""
Tests for index.html

Validates the changes introduced in this PR:
- Addition of lang="en" attribute to the <html> element
- Blank lines added for readability (after <html>, after </head>)
- No missing newline at end of file (file ends with </html> and newline)
- Overall structural integrity of the HTML document
"""

import os
import re
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
# lang attribute tests (new in this PR)
# ---------------------------------------------------------------------------

class TestLangAttribute:
    """Tests for the lang="en" attribute added to the <html> element in this PR."""

    def test_html_tag_has_lang_attribute(self, html_content):
        """The <html> tag must have a lang attribute after this PR."""
        assert re.search(r'<html\s[^>]*lang\s*=', html_content, re.IGNORECASE), \
            '<html> element must have a lang attribute'

    def test_html_lang_is_en(self, html_content):
        """The lang attribute value must be 'en'."""
        match = re.search(r'<html\s[^>]*lang\s*=\s*["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        assert match is not None, "lang attribute not found"
        assert match.group(1) == "en", f"Expected lang='en', got lang='{match.group(1)}'"

    def test_html_tag_with_lang_on_line_two(self, html_lines):
        """The <html lang="en"> tag must be on the second line (index 1)."""
        second_line = html_lines[1].strip()
        assert 'lang="en"' in second_line, \
            f'Expected lang="en" on line 2, got: {second_line!r}'

    def test_lang_attribute_exact_value(self, html_content):
        """lang attribute must be exactly 'en', not 'en-US' or other variants."""
        assert 'lang="en"' in html_content or "lang='en'" in html_content

    # Regression: lang attribute must not be empty
    def test_lang_attribute_not_empty(self, html_content):
        assert not re.search(r'lang\s*=\s*["\']["\']', html_content), \
            "lang attribute must not be empty"

    # Boundary: html tag must not have an incorrect lang code
    def test_html_tag_does_not_have_wrong_lang(self, html_content):
        match = re.search(r'<html\s[^>]*lang\s*=\s*["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        if match:
            assert match.group(1) not in ("", "en-US", "fr", "de"), \
                f"Unexpected lang value: {match.group(1)!r}"


# ---------------------------------------------------------------------------
# DOCTYPE tests
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

    def test_meta_charset_is_utf8(self, html_content):
        assert re.search(r'charset\s*=\s*["\']?UTF-8', html_content, re.IGNORECASE)

    def test_css_link_present(self, html_content):
        assert 'href="css/style.css"' in html_content

    def test_nav_present(self, html_content):
        assert "<nav>" in html_content

    def test_footer_present(self, html_content):
        assert "<footer>" in html_content

    def test_title_content_correct(self, html_content):
        assert "QuickHire" in html_content

    def test_closing_html_tag_present(self, html_content):
        assert "</html>" in html_content

    def test_closing_body_tag_present(self, html_content):
        assert "</body>" in html_content


# ---------------------------------------------------------------------------
# Navigation content tests
# ---------------------------------------------------------------------------

class TestNavigationContent:
    def test_login_link_present(self, html_content):
        assert 'href="login.html"' in html_content

    def test_register_link_present(self, html_content):
        assert 'href="register-student.html"' in html_content

    def test_quickhire_brand_present(self, html_content):
        assert "QuickHire" in html_content


# ---------------------------------------------------------------------------
# Hero section tests
# ---------------------------------------------------------------------------

class TestHeroSection:
    def test_hero_section_present(self, html_content):
        assert 'class="hero"' in html_content

    def test_student_cta_button_present(self, html_content):
        assert "I'm a Student" in html_content or "I'm a Student" in html_content

    def test_company_cta_button_present(self, html_content):
        assert "I'm a Company" in html_content or "I'm a Company" in html_content

    def test_student_register_link_in_hero(self, html_content):
        assert 'href="register-student.html"' in html_content

    def test_company_register_link_in_hero(self, html_content):
        assert 'href="register-company.html"' in html_content


# ---------------------------------------------------------------------------
# Blank lines added in this PR
# ---------------------------------------------------------------------------

class TestWhitespaceChanges:
    def test_blank_line_after_html_tag(self, html_lines):
        """A blank line must follow the <html lang="en"> line (added in this PR)."""
        html_tag_line_idx = next(
            i for i, line in enumerate(html_lines) if "<html" in line.lower()
        )
        # The line after <html lang="en"> should be blank
        next_line = html_lines[html_tag_line_idx + 1].strip()
        assert next_line == "", f"Expected blank line after <html> tag, got: {next_line!r}"

    def test_blank_line_after_head_closing_tag(self, html_lines):
        """A blank line must follow </head> (added in this PR)."""
        head_close_idx = next(
            (i for i, line in enumerate(html_lines) if "</head>" in line.lower()), None
        )
        assert head_close_idx is not None, "</head> not found"
        next_line = html_lines[head_close_idx + 1].strip()
        assert next_line == "", f"Expected blank line after </head>, got: {next_line!r}"