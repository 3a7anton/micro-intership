"""
Tests for js/supabase-client.js

Validates the changes introduced in this PR:
- Hardcoded Supabase credentials removed (previously had real URL + JWT anon key)
- SUPABASE_URL and SUPABASE_KEY now set to empty strings ''
- TODO comment added directing devs to use environment variables
- createClient call still present
"""

import os
import re
import pytest

JS_PATH = os.path.join(os.path.dirname(__file__), "..", "js", "supabase-client.js")


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
    def test_supabase_client_js_exists(self):
        assert os.path.isfile(JS_PATH), "js/supabase-client.js must exist"

    def test_file_is_not_empty(self):
        assert os.path.getsize(JS_PATH) > 0


# ---------------------------------------------------------------------------
# Credential removal tests (core change in this PR)
# ---------------------------------------------------------------------------

class TestCredentialRemoval:
    """Validate that hardcoded credentials were removed in this PR."""

    def test_no_hardcoded_supabase_url(self, js_content):
        """No real Supabase project URL should appear in the file."""
        assert "supabase.co" not in js_content, \
            "Hardcoded Supabase URL must not be present"

    def test_no_jwt_token(self, js_content):
        """No JWT token (eyJ...) should appear in the file."""
        assert not re.search(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', js_content), \
            "Hardcoded JWT token must not be present"

    def test_no_hardcoded_anon_key(self, js_content):
        """The previously hardcoded anon key must be removed."""
        # The old key was a long base64url-encoded JWT string
        old_key_fragment = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        assert old_key_fragment not in js_content, \
            "Previously hardcoded JWT header must be removed"

    def test_supabase_url_is_empty_string(self, js_content):
        """SUPABASE_URL should now be set to an empty string."""
        assert re.search(r"const\s+SUPABASE_URL\s*=\s*''", js_content) or \
               re.search(r'const\s+SUPABASE_URL\s*=\s*""', js_content), \
            "SUPABASE_URL must be set to empty string ''"

    def test_supabase_key_is_empty_string(self, js_content):
        """SUPABASE_KEY should now be set to an empty string."""
        assert re.search(r"const\s+SUPABASE_KEY\s*=\s*''", js_content) or \
               re.search(r'const\s+SUPABASE_KEY\s*=\s*""', js_content), \
            "SUPABASE_KEY must be set to empty string ''"

    def test_no_https_url_with_credentials(self, js_content):
        """No https URL pointing to a supabase project should be present."""
        assert not re.search(r'https://[a-z0-9]+\.supabase\.co', js_content), \
            "No hardcoded Supabase project URL allowed"

    # Boundary: ensure no attempt to store key in a comment (accident)
    def test_no_credential_in_comments(self, js_content):
        """JWT tokens must not appear anywhere, even in comments."""
        assert "eyJhbGciOi" not in js_content


# ---------------------------------------------------------------------------
# TODO comment tests (new in this PR)
# ---------------------------------------------------------------------------

class TestTodoComment:
    def test_todo_comment_present(self, js_content):
        """A TODO comment about environment variables must be present."""
        assert "TODO" in js_content, "TODO comment must be present"

    def test_todo_mentions_env_variables(self, js_content):
        """The TODO comment should mention environment variables."""
        assert "environment variable" in js_content.lower() or \
               "process.env" in js_content, \
            "TODO comment must mention environment variables"

    def test_todo_mentions_supabase_url(self, js_content):
        """The TODO comment should reference SUPABASE_URL."""
        assert "SUPABASE_URL" in js_content

    def test_todo_mentions_supabase_key(self, js_content):
        """The TODO comment should reference SUPABASE_KEY or SUPABASE_ANON_KEY."""
        assert "SUPABASE_KEY" in js_content or "SUPABASE_ANON_KEY" in js_content


# ---------------------------------------------------------------------------
# createClient usage tests (existing functionality preserved)
# ---------------------------------------------------------------------------

class TestCreateClientUsage:
    def test_create_client_destructured(self, js_content):
        """createClient must be destructured from the supabase object."""
        assert "const { createClient } = supabase" in js_content or \
               "const {createClient} = supabase" in js_content

    def test_supabase_client_created(self, js_content):
        """supabaseClient must be initialized by calling createClient."""
        assert re.search(r'const\s+supabaseClient\s*=\s*createClient\s*\(', js_content), \
            "supabaseClient must be created via createClient()"

    def test_create_client_receives_url_and_key(self, js_content):
        """createClient must be called with SUPABASE_URL and SUPABASE_KEY."""
        assert re.search(
            r'createClient\s*\(\s*SUPABASE_URL\s*,\s*SUPABASE_KEY\s*\)',
            js_content
        ), "createClient must receive SUPABASE_URL and SUPABASE_KEY as arguments"

    def test_supabase_client_variable_exported(self, js_content):
        """supabaseClient variable name must be present for other scripts to use."""
        assert "supabaseClient" in js_content

    # Regression: SUPABASE_URL declaration must still exist (not deleted)
    def test_supabase_url_declared(self, js_content):
        assert re.search(r'const\s+SUPABASE_URL\s*=', js_content)

    # Regression: SUPABASE_KEY declaration must still exist (not deleted)
    def test_supabase_key_declared(self, js_content):
        assert re.search(r'const\s+SUPABASE_KEY\s*=', js_content)