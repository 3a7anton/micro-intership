"""
Tests for .coderabbit.yaml

Validates the structure and values of the CodeRabbit configuration file
added in this PR.
"""

import os
import re
import pytest
import yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", ".coderabbit.yaml")


@pytest.fixture(scope="module")
def config():
    """Load and return the parsed .coderabbit.yaml configuration."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileValidity:
    def test_file_exists(self):
        assert os.path.isfile(CONFIG_PATH), ".coderabbit.yaml must exist"

    def test_file_is_valid_yaml(self):
        with open(CONFIG_PATH, "r") as f:
            parsed = yaml.safe_load(f)
        assert parsed is not None, "YAML file must not be empty"
        assert isinstance(parsed, dict), "Top-level YAML structure must be a mapping"

    def test_file_is_not_empty(self):
        assert os.path.getsize(CONFIG_PATH) > 0, ".coderabbit.yaml must not be empty"

    def test_file_has_no_tabs(self):
        """YAML files should use spaces, not tabs, for indentation."""
        with open(CONFIG_PATH, "r") as f:
            content = f.read()
        assert "\t" not in content, "YAML file must not contain tab characters"


# ---------------------------------------------------------------------------
# Top-level key tests
# ---------------------------------------------------------------------------

class TestTopLevelKeys:
    def test_language_key_present(self, config):
        assert "language" in config

    def test_reviews_key_present(self, config):
        assert "reviews" in config

    def test_chat_key_present(self, config):
        assert "chat" in config

    def test_language_value(self, config):
        assert config["language"] == "en-US"

    def test_language_is_string(self, config):
        assert isinstance(config["language"], str)

    def test_no_unexpected_top_level_keys(self, config):
        allowed = {"language", "reviews", "chat"}
        extra = set(config.keys()) - allowed
        assert not extra, f"Unexpected top-level keys: {extra}"


# ---------------------------------------------------------------------------
# reviews section
# ---------------------------------------------------------------------------

class TestReviewsSection:
    def test_reviews_is_mapping(self, config):
        assert isinstance(config["reviews"], dict)

    def test_profile_present(self, config):
        assert "profile" in config["reviews"]

    def test_profile_value(self, config):
        assert config["reviews"]["profile"] == "chill"

    def test_request_changes_workflow_present(self, config):
        assert "request_changes_workflow" in config["reviews"]

    def test_request_changes_workflow_is_false(self, config):
        assert config["reviews"]["request_changes_workflow"] is False

    def test_request_changes_workflow_is_boolean(self, config):
        assert isinstance(config["reviews"]["request_changes_workflow"], bool)

    def test_high_level_summary_is_true(self, config):
        assert config["reviews"]["high_level_summary"] is True

    def test_high_level_summary_is_boolean(self, config):
        assert isinstance(config["reviews"]["high_level_summary"], bool)

    def test_high_level_summary_placeholder(self, config):
        assert config["reviews"]["high_level_summary_placeholder"] == "@coderabbitai summary"

    def test_auto_title_placeholder(self, config):
        assert config["reviews"]["auto_title_placeholder"] == "@coderabbitai"

    def test_poem_is_false(self, config):
        assert config["reviews"]["poem"] is False

    def test_poem_is_boolean(self, config):
        assert isinstance(config["reviews"]["poem"], bool)

    def test_review_status_is_true(self, config):
        assert config["reviews"]["review_status"] is True

    def test_review_status_is_boolean(self, config):
        assert isinstance(config["reviews"]["review_status"], bool)

    def test_collapse_walkthrough_is_false(self, config):
        assert config["reviews"]["collapse_walkthrough"] is False

    def test_collapse_walkthrough_is_boolean(self, config):
        assert isinstance(config["reviews"]["collapse_walkthrough"], bool)

    def test_sequence_diagrams_is_true(self, config):
        assert config["reviews"]["sequence_diagrams"] is True

    def test_sequence_diagrams_is_boolean(self, config):
        assert isinstance(config["reviews"]["sequence_diagrams"], bool)

    def test_changed_files_summary_is_true(self, config):
        assert config["reviews"]["changed_files_summary"] is True

    def test_changed_files_summary_is_boolean(self, config):
        assert isinstance(config["reviews"]["changed_files_summary"], bool)

    def test_labeling_instructions_present(self, config):
        assert "labeling_instructions" in config["reviews"]

    def test_labeling_instructions_is_empty_list(self, config):
        assert config["reviews"]["labeling_instructions"] == []

    def test_labeling_instructions_is_list(self, config):
        assert isinstance(config["reviews"]["labeling_instructions"], list)


# ---------------------------------------------------------------------------
# path_filters
# ---------------------------------------------------------------------------

class TestPathFilters:
    @pytest.fixture(autouse=True)
    def filters(self, config):
        self._filters = config["reviews"]["path_filters"]

    def test_path_filters_present(self, config):
        assert "path_filters" in config["reviews"]

    def test_path_filters_is_list(self):
        assert isinstance(self._filters, list)

    def test_path_filters_not_empty(self):
        assert len(self._filters) > 0

    def test_all_filters_are_strings(self):
        assert all(isinstance(f, str) for f in self._filters)

    def test_excludes_minified_js(self):
        assert "!**/*.min.js" in self._filters

    def test_excludes_minified_css(self):
        assert "!**/*.min.css" in self._filters

    def test_excludes_node_modules(self):
        assert "!**/node_modules/**" in self._filters

    def test_excludes_git_directory(self):
        assert "!**/.git/**" in self._filters

    def test_all_filters_are_exclusions(self):
        """Every filter in this config should be a negation pattern."""
        assert all(f.startswith("!") for f in self._filters)

    def test_exactly_four_filters(self):
        assert len(self._filters) == 4

    def test_no_duplicate_filters(self):
        assert len(self._filters) == len(set(self._filters))


# ---------------------------------------------------------------------------
# path_instructions
# ---------------------------------------------------------------------------

class TestPathInstructions:
    @pytest.fixture(autouse=True)
    def instructions(self, config):
        self._instructions = config["reviews"]["path_instructions"]

    def test_path_instructions_present(self, config):
        assert "path_instructions" in config["reviews"]

    def test_path_instructions_is_list(self):
        assert isinstance(self._instructions, list)

    def test_path_instructions_not_empty(self):
        assert len(self._instructions) > 0

    def test_each_entry_has_path_key(self):
        for entry in self._instructions:
            assert "path" in entry, f"Entry missing 'path': {entry}"

    def test_each_entry_has_instructions_key(self):
        for entry in self._instructions:
            assert "instructions" in entry, f"Entry missing 'instructions': {entry}"

    def test_each_entry_has_exactly_two_keys(self):
        for entry in self._instructions:
            assert set(entry.keys()) == {"path", "instructions"}

    def test_all_paths_are_strings(self):
        for entry in self._instructions:
            assert isinstance(entry["path"], str)

    def test_all_instructions_are_strings(self):
        for entry in self._instructions:
            assert isinstance(entry["instructions"], str)

    def test_all_instructions_are_non_empty(self):
        for entry in self._instructions:
            assert entry["instructions"].strip(), f"Empty instructions for path: {entry['path']}"

    def _paths(self):
        return [entry["path"] for entry in self._instructions]

    def test_html_path_instruction_present(self):
        assert "**/*.html" in self._paths()

    def test_css_path_instruction_present(self):
        assert "css/**" in self._paths()

    def test_js_path_instruction_present(self):
        assert "js/**" in self._paths()

    def test_admin_path_instruction_present(self):
        assert "admin/**" in self._paths()

    def test_student_path_instruction_present(self):
        assert "student/**" in self._paths()

    def test_sql_path_instruction_present(self):
        assert "supabase-setup.sql" in self._paths()

    def test_html_instructions_mention_accessibility(self):
        html_entry = next(e for e in self._instructions if e["path"] == "**/*.html")
        instr = html_entry["instructions"].lower()
        assert "accessibility" in instr or "aria" in instr

    def test_html_instructions_mention_meta_tags(self):
        html_entry = next(e for e in self._instructions if e["path"] == "**/*.html")
        assert "meta" in html_entry["instructions"].lower()

    def test_js_instructions_mention_security(self):
        js_entry = next(e for e in self._instructions if e["path"] == "js/**")
        instr = js_entry["instructions"].lower()
        assert "security" in instr or "xss" in instr or "api key" in instr or "hardcoded" in instr

    def test_js_instructions_mention_error_handling(self):
        js_entry = next(e for e in self._instructions if e["path"] == "js/**")
        assert "error handling" in js_entry["instructions"].lower()

    def test_admin_instructions_mention_authorization(self):
        admin_entry = next(e for e in self._instructions if e["path"] == "admin/**")
        instr = admin_entry["instructions"].lower()
        assert "authorization" in instr or "admin" in instr or "rls" in instr

    def test_sql_instructions_mention_rls(self):
        sql_entry = next(e for e in self._instructions if e["path"] == "supabase-setup.sql")
        instr = sql_entry["instructions"].lower()
        assert "rls" in instr or "row level security" in instr

    def test_sql_instructions_mention_foreign_key(self):
        sql_entry = next(e for e in self._instructions if e["path"] == "supabase-setup.sql")
        assert "foreign key" in sql_entry["instructions"].lower()

    def test_no_duplicate_paths(self):
        paths = self._paths()
        assert len(paths) == len(set(paths)), "Duplicate path entries found"

    def test_exactly_six_path_instructions(self):
        assert len(self._instructions) == 6


# ---------------------------------------------------------------------------
# auto_review section
# ---------------------------------------------------------------------------

class TestAutoReview:
    @pytest.fixture(autouse=True)
    def auto_review(self, config):
        self._ar = config["reviews"]["auto_review"]

    def test_auto_review_present(self, config):
        assert "auto_review" in config["reviews"]

    def test_auto_review_is_mapping(self):
        assert isinstance(self._ar, dict)

    def test_enabled_present(self):
        assert "enabled" in self._ar

    def test_enabled_is_true(self):
        assert self._ar["enabled"] is True

    def test_enabled_is_boolean(self):
        assert isinstance(self._ar["enabled"], bool)

    def test_drafts_present(self):
        assert "drafts" in self._ar

    def test_drafts_is_false(self):
        assert self._ar["drafts"] is False

    def test_drafts_is_boolean(self):
        assert isinstance(self._ar["drafts"], bool)

    def test_base_branches_present(self):
        assert "base_branches" in self._ar

    def test_base_branches_is_list(self):
        assert isinstance(self._ar["base_branches"], list)

    def test_base_branches_not_empty(self):
        assert len(self._ar["base_branches"]) > 0

    def test_base_branches_includes_main(self):
        assert "main" in self._ar["base_branches"]

    def test_base_branches_includes_master(self):
        assert "master" in self._ar["base_branches"]

    def test_base_branches_no_duplicates(self):
        branches = self._ar["base_branches"]
        assert len(branches) == len(set(branches))

    def test_base_branches_are_non_empty_strings(self):
        for branch in self._ar["base_branches"]:
            assert isinstance(branch, str) and branch.strip()

    def test_exactly_two_base_branches(self):
        assert len(self._ar["base_branches"]) == 2


# ---------------------------------------------------------------------------
# chat section
# ---------------------------------------------------------------------------

class TestChatSection:
    def test_chat_is_mapping(self, config):
        assert isinstance(config["chat"], dict)

    def test_auto_reply_present(self, config):
        assert "auto_reply" in config["chat"]

    def test_auto_reply_is_true(self, config):
        assert config["chat"]["auto_reply"] is True

    def test_auto_reply_is_boolean(self, config):
        # Must be an actual bool, not a truthy string like "true"
        assert isinstance(config["chat"]["auto_reply"], bool)

    def test_chat_has_auto_reply_only(self, config):
        assert set(config["chat"].keys()) == {"auto_reply"}