"""
Tests for js/supabase-client.js

Validates the change introduced in this PR: hardcoded Supabase URL and API key
have been removed and replaced with empty strings, preventing credential exposure.
"""

import os
import re
import pytest

JS_PATH = os.path.join(os.path.dirname(__file__), "..", "js", "supabase-client.js")

# The old hardcoded values that must no longer be present
_OLD_SUPABASE_URL_FRAGMENT = "cnexjwkuraaqhcpzqzkx.supabase.co"
# Supabase anon JWTs start with "eyJ" and are long (>100 chars)
_JWT_PATTERN = re.compile(r'eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}')


@pytest.fixture(scope="module")
def js_content():
    """Return the full text of js/supabase-client.js."""
    with open(JS_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def js_lines():
    """Return the lines of js/supabase-client.js."""
    with open(JS_PATH, "r", encoding="utf-8") as f:
        return f.readlines()


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileExists:
    def test_file_exists(self):
        assert os.path.isfile(JS_PATH), "js/supabase-client.js must exist"

    def test_file_is_not_empty(self):
        assert os.path.getsize(JS_PATH) > 0


# ---------------------------------------------------------------------------
# Hardcoded credential removal tests (key change in this PR)
# ---------------------------------------------------------------------------

class TestNoHardcodedCredentials:
    """The PR replaced hardcoded Supabase URL and key with empty strings."""

    def test_no_hardcoded_supabase_url(self, js_content):
        assert _OLD_SUPABASE_URL_FRAGMENT not in js_content, (
            "Hardcoded Supabase project URL must not be present in the source file"
        )

    def test_no_jwt_token_present(self, js_content):
        """No JWT-formatted token (anon key) should appear in the file."""
        assert not _JWT_PATTERN.search(js_content), (
            "A JWT-formatted API key must not be hardcoded in supabase-client.js"
        )

    def test_supabase_url_is_empty_string(self, js_content):
        """SUPABASE_URL must be assigned an empty string, not a real URL."""
        match = re.search(r"const\s+SUPABASE_URL\s*=\s*'([^']*)'", js_content)
        assert match is not None, "SUPABASE_URL constant not found"
        assert match.group(1) == "", (
            f"SUPABASE_URL must be '' (empty), got: {match.group(1)!r}"
        )

    def test_supabase_key_is_empty_string(self, js_content):
        """SUPABASE_KEY must be assigned an empty string, not a real key."""
        match = re.search(r"const\s+SUPABASE_KEY\s*=\s*'([^']*)'", js_content)
        assert match is not None, "SUPABASE_KEY constant not found"
        assert match.group(1) == "", (
            f"SUPABASE_KEY must be '' (empty), got: {match.group(1)!r}"
        )

    # Boundary: also check double-quote form
    def test_supabase_url_not_a_real_url_double_quotes(self, js_content):
        match = re.search(r'const\s+SUPABASE_URL\s*=\s*"([^"]*)"', js_content)
        if match:
            assert match.group(1) == "", (
                "SUPABASE_URL must be empty if using double quotes"
            )

    def test_supabase_key_not_a_real_key_double_quotes(self, js_content):
        match = re.search(r'const\s+SUPABASE_KEY\s*=\s*"([^"]*)"', js_content)
        if match:
            assert match.group(1) == "", (
                "SUPABASE_KEY must be empty if using double quotes"
            )

    # Regression: supabase.co domain should not appear anywhere in the file
    def test_no_supabase_co_domain(self, js_content):
        assert ".supabase.co" not in js_content, (
            "No supabase.co project URL should be hardcoded"
        )


# ---------------------------------------------------------------------------
# TODO comment presence tests
# ---------------------------------------------------------------------------

class TestTodoComment:
    """The PR added a TODO comment directing developers to use env variables."""

    def test_todo_comment_present(self, js_content):
        assert "TODO" in js_content, (
            "A TODO comment about environment variables must be present"
        )

    def test_todo_mentions_environment_variables(self, js_content):
        assert "environment" in js_content.lower() or "env" in js_content.lower(), (
            "TODO comment should reference environment variables"
        )


# ---------------------------------------------------------------------------
# Supabase client initialisation tests
# ---------------------------------------------------------------------------

class TestClientInitialisation:
    """The file must still initialise the Supabase client correctly."""

    def test_create_client_call_present(self, js_content):
        assert "createClient" in js_content

    def test_supabase_client_variable_declared(self, js_content):
        assert "supabaseClient" in js_content

    def test_create_client_uses_url_and_key_constants(self, js_content):
        """createClient must be called with the SUPABASE_URL and SUPABASE_KEY constants."""
        assert re.search(
            r"createClient\s*\(\s*SUPABASE_URL\s*,\s*SUPABASE_KEY\s*\)", js_content
        ), "createClient must be called with SUPABASE_URL and SUPABASE_KEY"

    def test_supabase_destructure_present(self, js_content):
        """The file must destructure createClient from the supabase global."""
        assert re.search(
            r"const\s*\{\s*createClient\s*\}\s*=\s*supabase", js_content
        ), "createClient must be destructured from the supabase global"

    # Boundary: SUPABASE_URL constant must be declared with const
    def test_supabase_url_declared_with_const(self, js_content):
        assert re.search(r"\bconst\s+SUPABASE_URL\b", js_content)

    def test_supabase_key_declared_with_const(self, js_content):
        assert re.search(r"\bconst\s+SUPABASE_KEY\b", js_content)