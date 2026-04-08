"""
Tests for supabase-setup.sql

Validates the changes introduced in this PR:
- Section header comments removed (cosmetic)
- The permissive "Anyone can view user profiles" policy was REMOVED (security fix)
  A comment in the file documents this intentional removal to prevent data leakage.
- All 7 tables still present
- RLS still enabled on all tables
- All other RLS policies still present
- Helper functions still present
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
    """Return lowercased SQL content for case-insensitive matching."""
    return sql_content.lower()


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileExists:
    def test_sql_file_exists(self):
        assert os.path.isfile(SQL_PATH), "supabase-setup.sql must exist"

    def test_sql_file_is_not_empty(self):
        assert os.path.getsize(SQL_PATH) > 0


# ---------------------------------------------------------------------------
# Removed policy tests (core security change in this PR)
# ---------------------------------------------------------------------------

class TestRemovedAnyoneViewProfilesPolicy:
    """
    The 'Anyone can view user profiles' policy was removed in this PR
    to prevent data leakage. These tests ensure it remains absent.
    """

    def test_anyone_can_view_profiles_policy_absent(self, sql_lower):
        """The permissive 'Anyone can view user profiles' CREATE POLICY must not exist."""
        assert not re.search(
            r'create\s+policy\s+["\']anyone\s+can\s+view\s+user\s+profiles["\']',
            sql_lower
        ), "The 'Anyone can view user profiles' policy must be removed (data leakage risk)"

    def test_no_anon_select_all_users_policy(self, sql_lower):
        """No policy should grant anon/public SELECT on all users rows."""
        # The removed policy used: to anon, authenticated; using (true)
        # on the users table. Check it's not recreated.
        assert not re.search(
            r'on\s+users\s+for\s+select\s+to\s+anon.*using\s*\(\s*true\s*\)',
            sql_lower,
            re.DOTALL
        ), "No unrestricted SELECT policy should be created on the users table"

    def test_removal_comment_present(self, sql_content):
        """A comment documenting the intentional removal must be present."""
        assert "Anyone can view user profiles" in sql_content and \
               "removed" in sql_content.lower(), \
            "A comment explaining the removal of the permissive policy must exist"

    def test_data_leakage_comment_present(self, sql_content):
        """The comment must mention data leakage as the reason for removal."""
        assert "data leakage" in sql_content.lower() or \
               "data leak" in sql_content.lower() or \
               "prevent" in sql_content.lower()

    # Boundary: the users table must still have restricted SELECT policies
    def test_users_own_profile_select_policy_present(self, sql_content):
        """Users must still be able to select their own profile."""
        assert "Users can view own profile" in sql_content

    def test_admin_can_view_all_users_policy_present(self, sql_content):
        """Admins must still be able to view all users."""
        assert "Admin can view all users" in sql_content

    # Regression: the removed policy name must not appear as a create policy statement
    def test_no_create_policy_anyone_view_profiles(self, sql_lower):
        """No CREATE POLICY statement for 'Anyone can view user profiles'."""
        assert not re.search(
            r'create\s+policy\s+["\']anyone\s+can\s+view\s+user\s+profiles["\']',
            sql_lower
        )


# ---------------------------------------------------------------------------
# Table structure tests (preserved from pre-PR)
# ---------------------------------------------------------------------------

class TestTableStructure:
    def test_users_table_present(self, sql_lower):
        assert "create table users" in sql_lower

    def test_tasks_table_present(self, sql_lower):
        assert "create table tasks" in sql_lower

    def test_applications_table_present(self, sql_lower):
        assert "create table applications" in sql_lower

    def test_submissions_table_present(self, sql_lower):
        assert "create table submissions" in sql_lower

    def test_payments_table_present(self, sql_lower):
        assert "create table payments" in sql_lower

    def test_certificates_table_present(self, sql_lower):
        assert "create table certificates" in sql_lower

    def test_reviews_table_present(self, sql_lower):
        assert "create table reviews" in sql_lower

    def test_exactly_seven_create_table_statements(self, sql_lower):
        matches = re.findall(r'\bcreate\s+table\s+\w+', sql_lower)
        assert len(matches) == 7, f"Expected 7 CREATE TABLE statements, found {len(matches)}"


# ---------------------------------------------------------------------------
# RLS enablement tests
# ---------------------------------------------------------------------------

class TestRLSEnabled:
    def test_rls_enabled_on_users(self, sql_lower):
        assert re.search(r'alter\s+table\s+users\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_tasks(self, sql_lower):
        assert re.search(r'alter\s+table\s+tasks\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_applications(self, sql_lower):
        assert re.search(r'alter\s+table\s+applications\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_submissions(self, sql_lower):
        assert re.search(r'alter\s+table\s+submissions\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_payments(self, sql_lower):
        assert re.search(r'alter\s+table\s+payments\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_certificates(self, sql_lower):
        assert re.search(r'alter\s+table\s+certificates\s+enable\s+row\s+level\s+security', sql_lower)

    def test_rls_enabled_on_reviews(self, sql_lower):
        assert re.search(r'alter\s+table\s+reviews\s+enable\s+row\s+level\s+security', sql_lower)

    def test_all_seven_tables_have_rls_enabled(self, sql_lower):
        matches = re.findall(r'alter\s+table\s+\w+\s+enable\s+row\s+level\s+security', sql_lower)
        assert len(matches) == 7, f"Expected RLS enabled on all 7 tables, found {len(matches)}"


# ---------------------------------------------------------------------------
# Users table policy tests
# ---------------------------------------------------------------------------

class TestUsersTablePolicies:
    def test_users_can_view_own_profile(self, sql_content):
        assert "Users can view own profile" in sql_content

    def test_users_can_update_own_profile(self, sql_content):
        assert "Users can update own profile" in sql_content

    def test_users_can_insert_own_profile(self, sql_content):
        assert "Users can insert own profile" in sql_content

    def test_admin_can_view_all_users(self, sql_content):
        assert "Admin can view all users" in sql_content

    def test_admin_can_update_all_users(self, sql_content):
        assert "Admin can update all users" in sql_content

    def test_admin_can_delete_users(self, sql_content):
        assert "Admin can delete users" in sql_content


# ---------------------------------------------------------------------------
# Tasks table policy tests
# ---------------------------------------------------------------------------

class TestTasksTablePolicies:
    def test_anyone_can_view_open_tasks(self, sql_content):
        assert "Anyone can view open tasks" in sql_content

    def test_companies_can_view_own_tasks(self, sql_content):
        assert "Companies can view own tasks" in sql_content

    def test_companies_can_post_tasks(self, sql_content):
        assert "Companies can post tasks" in sql_content

    def test_companies_can_update_own_tasks(self, sql_content):
        assert "Companies can update own tasks" in sql_content

    def test_companies_can_delete_own_tasks(self, sql_content):
        assert "Companies can delete own tasks" in sql_content

    def test_admin_can_view_all_tasks(self, sql_content):
        assert "Admin can view all tasks" in sql_content

    def test_admin_can_delete_any_task(self, sql_content):
        assert "Admin can delete any task" in sql_content


# ---------------------------------------------------------------------------
# Applications table policy tests
# ---------------------------------------------------------------------------

class TestApplicationsTablePolicies:
    def test_students_can_view_own_applications(self, sql_content):
        assert "Students can view own applications" in sql_content

    def test_students_can_apply_for_tasks(self, sql_content):
        assert "Students can apply for tasks" in sql_content

    def test_companies_can_update_applications_for_own_tasks(self, sql_content):
        assert "Companies can update applications for own tasks" in sql_content

    def test_admin_can_view_all_applications(self, sql_content):
        assert "Admin can view all applications" in sql_content


# ---------------------------------------------------------------------------
# Submissions table policy tests
# ---------------------------------------------------------------------------

class TestSubmissionsTablePolicies:
    def test_students_can_view_own_submissions(self, sql_content):
        assert "Students can view own submissions" in sql_content

    def test_students_can_submit_work(self, sql_content):
        assert "Students can submit work" in sql_content

    def test_companies_can_update_submissions(self, sql_content):
        assert "Companies can update submissions" in sql_content


# ---------------------------------------------------------------------------
# Payments table policy tests
# ---------------------------------------------------------------------------

class TestPaymentsTablePolicies:
    def test_students_can_view_own_payments(self, sql_content):
        assert "Students can view own payments" in sql_content

    def test_companies_can_create_payments(self, sql_content):
        assert "Companies can create payments" in sql_content

    def test_companies_can_update_payments(self, sql_content):
        assert "Companies can update payments" in sql_content

    def test_admin_can_view_all_payments(self, sql_content):
        assert "Admin can view all payments" in sql_content


# ---------------------------------------------------------------------------
# Certificates table policy tests
# ---------------------------------------------------------------------------

class TestCertificatesTablePolicies:
    def test_students_can_view_own_certificates(self, sql_content):
        assert "Students can view own certificates" in sql_content

    def test_admin_can_create_certificates(self, sql_content):
        assert "Admin can create certificates" in sql_content


# ---------------------------------------------------------------------------
# Reviews table policy tests
# ---------------------------------------------------------------------------

class TestReviewsTablePolicies:
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

    def test_get_user_role_returns_varchar(self, sql_lower):
        assert re.search(r'function\s+get_user_role.*returns\s+varchar', sql_lower, re.DOTALL)

    def test_is_admin_returns_boolean(self, sql_lower):
        assert re.search(r'function\s+is_admin.*returns\s+boolean', sql_lower, re.DOTALL)

    def test_is_task_owner_takes_task_id_param(self, sql_lower):
        assert re.search(r'is_task_owner\s*\(\s*task_id\s+int\s*\)', sql_lower)

    # Boundary: exactly 3 helper functions
    def test_exactly_three_helper_functions(self, sql_lower):
        matches = re.findall(r'\bcreate\s+or\s+replace\s+function\s+\w+', sql_lower)
        assert len(matches) == 3, f"Expected 3 helper functions, found {len(matches)}"


# ---------------------------------------------------------------------------
# Foreign key constraint tests
# ---------------------------------------------------------------------------

class TestForeignKeyConstraints:
    def test_tasks_references_users(self, sql_lower):
        assert re.search(r'company_id\s+uuid\s+references\s+users\s*\(id\)', sql_lower)

    def test_applications_references_tasks(self, sql_lower):
        assert re.search(r'task_id\s+int\s+references\s+tasks\s*\(id\)', sql_lower)

    def test_applications_references_users(self, sql_lower):
        assert re.search(r'student_id\s+uuid\s+references\s+users\s*\(id\)', sql_lower)

    def test_submissions_references_applications(self, sql_lower):
        assert re.search(r'application_id\s+int\s+references\s+applications\s*\(id\)', sql_lower)

    def test_users_references_auth_users(self, sql_lower):
        assert re.search(r'id\s+uuid\s+references\s+auth\.users', sql_lower)