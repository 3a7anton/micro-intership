"""
Tests for supabase-setup.sql

Validates the changes introduced in this PR:
- The overly-permissive policy 'Anyone can view user profiles' has been removed
  to prevent data leakage.
- All required tables are still created.
- RLS is still enabled on all tables.
- Essential security policies (users can view/update/insert own profile, admin
  policies) are still present.
- SQL helper functions are still defined.
"""

import os
import re
import pytest

SQL_PATH = os.path.join(os.path.dirname(__file__), "..", "supabase-setup.sql")


@pytest.fixture(scope="module")
def sql_content():
    """Return the full text of supabase-setup.sql."""
    with open(SQL_PATH, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def sql_lower(sql_content):
    return sql_content.lower()


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileExists:
    def test_file_exists(self):
        assert os.path.isfile(SQL_PATH), "supabase-setup.sql must exist"

    def test_file_is_not_empty(self):
        assert os.path.getsize(SQL_PATH) > 0


# ---------------------------------------------------------------------------
# Removed policy tests (core security change in this PR)
# ---------------------------------------------------------------------------

class TestRemovedPermissivePolicy:
    """The 'Anyone can view user profiles' policy was removed to prevent data leakage."""

    def test_anyone_can_view_user_profiles_policy_absent(self, sql_content):
        """This overly-permissive policy must not exist as a CREATE POLICY statement."""
        import re
        # The policy name may appear in a comment explaining its removal, so we check
        # for the absence of an actual CREATE POLICY statement using that name.
        pattern = re.compile(
            r'create\s+policy\s+"Anyone can view user profiles"',
            re.IGNORECASE,
        )
        assert not pattern.search(sql_content), (
            "The permissive 'Anyone can view user profiles' CREATE POLICY must have been removed"
        )

    def test_no_anon_select_on_users_with_true(self, sql_content):
        """
        The removed policy granted anon+authenticated SELECT on users using(true).
        Verify this exact pattern is absent.
        """
        # Pattern: FOR SELECT TO anon ... USING (true)
        pattern = re.compile(
            r"on\s+users\s+for\s+select\s+to\s+(anon|authenticated).*?using\s*\(\s*true\s*\)",
            re.IGNORECASE | re.DOTALL,
        )
        assert not pattern.search(sql_content), (
            "A permissive SELECT policy on users with USING(true) must not be present"
        )

    def test_comment_explains_removal(self, sql_content):
        """A comment explaining the policy removal should be present."""
        assert "permissive" in sql_content.lower() or "data leakage" in sql_content.lower(), (
            "A comment explaining the removal of the permissive policy should be present"
        )

    # Boundary: ensure the change comment references the removed policy name
    def test_removal_comment_references_anyone_can_view(self, sql_content):
        assert "Anyone can view user profiles" in sql_content or (
            "permissive" in sql_content.lower() and "profile" in sql_content.lower()
        ), "Comment should reference the removed permissive user profile policy"


# ---------------------------------------------------------------------------
# Table creation tests
# ---------------------------------------------------------------------------

class TestTableCreation:
    EXPECTED_TABLES = [
        "users",
        "tasks",
        "applications",
        "submissions",
        "payments",
        "certificates",
        "reviews",
    ]

    @pytest.mark.parametrize("table", EXPECTED_TABLES)
    def test_table_created(self, table, sql_lower):
        assert f"create table {table}" in sql_lower, (
            f"CREATE TABLE {table} must be present"
        )

    def test_all_seven_tables_present(self, sql_lower):
        count = sum(
            1 for t in self.EXPECTED_TABLES if f"create table {t}" in sql_lower
        )
        assert count == len(self.EXPECTED_TABLES)


# ---------------------------------------------------------------------------
# RLS enablement tests
# ---------------------------------------------------------------------------

class TestRLSEnabled:
    EXPECTED_TABLES = [
        "users",
        "tasks",
        "applications",
        "submissions",
        "payments",
        "certificates",
        "reviews",
    ]

    @pytest.mark.parametrize("table", EXPECTED_TABLES)
    def test_rls_enabled_on_table(self, table, sql_lower):
        assert f"alter table {table} enable row level security" in sql_lower, (
            f"RLS must be enabled on table {table}"
        )

    def test_rls_enabled_on_all_tables(self, sql_lower):
        count = sum(
            1
            for t in self.EXPECTED_TABLES
            if f"alter table {t} enable row level security" in sql_lower
        )
        assert count == len(self.EXPECTED_TABLES)


# ---------------------------------------------------------------------------
# Users table policy tests
# ---------------------------------------------------------------------------

class TestUsersPolicies:
    """Verify the security policies on the users table are correct post-PR."""

    def test_users_can_view_own_profile_policy_present(self, sql_content):
        assert "Users can view own profile" in sql_content

    def test_users_can_update_own_profile_policy_present(self, sql_content):
        assert "Users can update own profile" in sql_content

    def test_users_can_insert_own_profile_policy_present(self, sql_content):
        assert "Users can insert own profile" in sql_content

    def test_admin_can_view_all_users_policy_present(self, sql_content):
        assert "Admin can view all users" in sql_content

    def test_admin_can_update_all_users_policy_present(self, sql_content):
        assert "Admin can update all users" in sql_content

    def test_admin_can_delete_users_policy_present(self, sql_content):
        assert "Admin can delete users" in sql_content

    def test_view_own_profile_uses_auth_uid(self, sql_content):
        """The own-profile SELECT policy must use auth.uid() = id."""
        pattern = re.compile(
            r'"Users can view own profile".*?using\s*\(\s*auth\.uid\(\)\s*=\s*id\s*\)',
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(sql_content), (
            "'Users can view own profile' must use USING (auth.uid() = id)"
        )

    def test_insert_own_profile_uses_with_check(self, sql_content):
        """The own-profile INSERT policy must use WITH CHECK."""
        pattern = re.compile(
            r'"Users can insert own profile".*?with\s+check\s*\(\s*auth\.uid\(\)\s*=\s*id\s*\)',
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(sql_content), (
            "'Users can insert own profile' must use WITH CHECK (auth.uid() = id)"
        )

    # Boundary: admin policies must query role = 'admin'
    def test_admin_view_policy_checks_admin_role(self, sql_content):
        pattern = re.compile(
            r'"Admin can view all users".*?role\s*=\s*\'admin\'',
            re.IGNORECASE | re.DOTALL,
        )
        assert pattern.search(sql_content)

    # Regression: exactly the right number of SELECT policies on users
    # (after removal: 2 SELECT policies remain - "view own profile" + "admin view all")
    def test_two_select_policies_on_users(self, sql_content):
        """After removing the permissive policy, exactly 2 SELECT policies should remain on users."""
        # Find all policy blocks targeting the users table with for select
        blocks = re.findall(
            r'create policy[^;]+on\s+users\s+for\s+select[^;]+;',
            sql_content,
            re.IGNORECASE | re.DOTALL,
        )
        assert len(blocks) == 2, (
            f"Expected exactly 2 SELECT policies on users table, found {len(blocks)}: "
            + str([re.search(r'"([^"]+)"', b).group(1) for b in blocks if re.search(r'"([^"]+)"', b)])
        )


# ---------------------------------------------------------------------------
# Tasks table policy tests
# ---------------------------------------------------------------------------

class TestTasksPolicies:
    EXPECTED_TASK_POLICIES = [
        "Anyone can view open tasks",
        "Companies can view own tasks",
        "Companies can post tasks",
        "Companies can update own tasks",
        "Companies can delete own tasks",
        "Admin can view all tasks",
        "Admin can delete any task",
    ]

    @pytest.mark.parametrize("policy", EXPECTED_TASK_POLICIES)
    def test_task_policy_present(self, policy, sql_content):
        assert policy in sql_content, f"Policy '{policy}' must be present"


# ---------------------------------------------------------------------------
# Applications table policy tests
# ---------------------------------------------------------------------------

class TestApplicationsPolicies:
    def test_students_can_view_own_applications(self, sql_content):
        assert "Students can view own applications" in sql_content

    def test_students_can_apply_for_tasks(self, sql_content):
        assert "Students can apply for tasks" in sql_content

    def test_companies_can_update_applications(self, sql_content):
        assert "Companies can update applications for own tasks" in sql_content

    def test_admin_can_view_all_applications(self, sql_content):
        assert "Admin can view all applications" in sql_content


# ---------------------------------------------------------------------------
# Submissions, payments, certificates, reviews policy smoke tests
# ---------------------------------------------------------------------------

class TestOtherTablePolicies:
    def test_students_can_view_own_submissions(self, sql_content):
        assert "Students can view own submissions" in sql_content

    def test_students_can_submit_work(self, sql_content):
        assert "Students can submit work" in sql_content

    def test_companies_can_update_submissions(self, sql_content):
        assert "Companies can update submissions" in sql_content

    def test_students_can_view_own_payments(self, sql_content):
        assert "Students can view own payments" in sql_content

    def test_companies_can_create_payments(self, sql_content):
        assert "Companies can create payments" in sql_content

    def test_admin_can_view_all_payments(self, sql_content):
        assert "Admin can view all payments" in sql_content

    def test_students_can_view_own_certificates(self, sql_content):
        assert "Students can view own certificates" in sql_content

    def test_admin_can_create_certificates(self, sql_content):
        assert "Admin can create certificates" in sql_content

    def test_anyone_can_view_reviews(self, sql_content):
        assert "Anyone can view reviews" in sql_content

    def test_users_can_create_reviews(self, sql_content):
        assert "Users can create reviews" in sql_content

    def test_users_can_update_own_reviews(self, sql_content):
        assert "Users can update own reviews" in sql_content


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------

class TestHelperFunctions:
    def test_get_user_role_function_present(self, sql_lower):
        assert "get_user_role" in sql_lower

    def test_is_admin_function_present(self, sql_lower):
        assert "is_admin" in sql_lower

    def test_is_task_owner_function_present(self, sql_lower):
        assert "is_task_owner" in sql_lower

    def test_functions_use_security_definer(self, sql_lower):
        assert "security definer" in sql_lower

    # Boundary: functions must be created with CREATE OR REPLACE
    def test_get_user_role_uses_create_or_replace(self, sql_lower):
        assert re.search(
            r"create or replace function get_user_role", sql_lower
        )

    def test_is_admin_uses_create_or_replace(self, sql_lower):
        assert re.search(
            r"create or replace function is_admin", sql_lower
        )

    def test_is_task_owner_uses_create_or_replace(self, sql_lower):
        assert re.search(
            r"create or replace function is_task_owner", sql_lower
        )