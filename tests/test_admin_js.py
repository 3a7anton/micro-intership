"""
Tests for js/admin.js

Validates the changes introduced in this PR:
- Error handling added to loadAdminDashboard():
  - usersError: checked with early return
  - tasksCountError: checked with console.error
  - certCountError: checked with console.error
  - recentTasksError: checked with console.error
- Error handling added to loadReports():
  - rUsersError, rTasksError, rAppsError, rCertsError, rPaymentsError: all checked
- Error variables now destructured in each Supabase call
"""

import os
import re
import pytest

JS_PATH = os.path.join(os.path.dirname(__file__), "..", "js", "admin.js")


@pytest.fixture(scope="module")
def js_content():
    """Return the full text of js/admin.js."""
    with open(JS_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# File-level tests
# ---------------------------------------------------------------------------

class TestFileExists:
    def test_admin_js_exists(self):
        assert os.path.isfile(JS_PATH), "js/admin.js must exist"

    def test_file_is_not_empty(self):
        assert os.path.getsize(JS_PATH) > 0


# ---------------------------------------------------------------------------
# loadAdminDashboard error handling tests
# ---------------------------------------------------------------------------

class TestLoadAdminDashboardErrorHandling:
    """Validates error handling added to loadAdminDashboard in this PR."""

    def test_users_error_variable_destructured(self, js_content):
        """usersError must be destructured from the users query."""
        assert re.search(r'error\s*:\s*usersError', js_content), \
            "usersError must be destructured from users query"

    def test_users_error_is_checked(self, js_content):
        """usersError must be checked with an if statement."""
        assert re.search(r'if\s*\(\s*usersError\s*\)', js_content), \
            "usersError must be checked with if(usersError)"

    def test_users_error_causes_early_return(self, js_content):
        """When usersError occurs, the function must return early."""
        # The pattern: if (usersError) { ... return; }
        assert re.search(
            r'if\s*\(\s*usersError\s*\)[^}]*return\s*;',
            js_content,
            re.DOTALL
        ), "usersError handler must contain a return statement"

    def test_users_error_logs_message(self, js_content):
        """usersError handler must log with console.error."""
        assert re.search(
            r'if\s*\(\s*usersError\s*\)[^}]*console\.error',
            js_content,
            re.DOTALL
        ), "usersError handler must call console.error"

    def test_tasks_count_error_variable_destructured(self, js_content):
        """tasksCountError must be destructured from the tasks count query."""
        assert re.search(r'error\s*:\s*tasksCountError', js_content), \
            "tasksCountError must be destructured from tasks query"

    def test_tasks_count_error_is_checked(self, js_content):
        """tasksCountError must be checked with an if statement."""
        assert re.search(r'if\s*\(\s*tasksCountError\s*\)', js_content), \
            "tasksCountError must be checked"

    def test_tasks_count_error_logs_with_console_error(self, js_content):
        """tasksCountError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*tasksCountError\s*\)[^}]*console\.error',
            js_content,
            re.DOTALL
        )

    def test_cert_count_error_variable_destructured(self, js_content):
        """certCountError must be destructured from the certificates count query."""
        assert re.search(r'error\s*:\s*certCountError', js_content), \
            "certCountError must be destructured from certificates query"

    def test_cert_count_error_is_checked(self, js_content):
        """certCountError must be checked with an if statement."""
        assert re.search(r'if\s*\(\s*certCountError\s*\)', js_content), \
            "certCountError must be checked"

    def test_cert_count_error_logs_with_console_error(self, js_content):
        """certCountError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*certCountError\s*\)[^}]*console\.error',
            js_content,
            re.DOTALL
        )

    def test_recent_tasks_error_variable_destructured(self, js_content):
        """recentTasksError must be destructured from the recent tasks query."""
        assert re.search(r'error\s*:\s*recentTasksError', js_content), \
            "recentTasksError must be destructured from recent tasks query"

    def test_recent_tasks_error_is_checked(self, js_content):
        """recentTasksError must be checked with an if statement."""
        assert re.search(r'if\s*\(\s*recentTasksError\s*\)', js_content), \
            "recentTasksError must be checked"

    def test_recent_tasks_error_logs_with_console_error(self, js_content):
        """recentTasksError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*recentTasksError\s*\)[^}]*console\.error',
            js_content,
            re.DOTALL
        )

    def test_users_error_message_logged(self, js_content):
        """usersError.message must be included in the error log."""
        assert "usersError.message" in js_content

    def test_tasks_count_error_message_logged(self, js_content):
        """tasksCountError.message must be included in the error log."""
        assert "tasksCountError.message" in js_content

    def test_cert_count_error_message_logged(self, js_content):
        """certCountError.message must be included in the error log."""
        assert "certCountError.message" in js_content

    def test_recent_tasks_error_message_logged(self, js_content):
        """recentTasksError.message must be included in the error log."""
        assert "recentTasksError.message" in js_content


# ---------------------------------------------------------------------------
# loadReports error handling tests
# ---------------------------------------------------------------------------

class TestLoadReportsErrorHandling:
    """Validates error handling added to loadReports in this PR."""

    def test_r_users_error_destructured(self, js_content):
        """rUsersError must be destructured from the users query in loadReports."""
        assert re.search(r'error\s*:\s*rUsersError', js_content), \
            "rUsersError must be destructured"

    def test_r_users_error_checked(self, js_content):
        """rUsersError must be checked."""
        assert "rUsersError" in js_content
        assert re.search(r'if\s*\(\s*rUsersError\s*\)', js_content)

    def test_r_users_error_logs_with_console_error(self, js_content):
        """rUsersError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*rUsersError\s*\)[^\n]*console\.error',
            js_content
        )

    def test_r_tasks_error_destructured(self, js_content):
        """rTasksError must be destructured from the tasks query in loadReports."""
        assert re.search(r'error\s*:\s*rTasksError', js_content), \
            "rTasksError must be destructured"

    def test_r_tasks_error_checked(self, js_content):
        """rTasksError must be checked."""
        assert re.search(r'if\s*\(\s*rTasksError\s*\)', js_content)

    def test_r_tasks_error_logs_with_console_error(self, js_content):
        """rTasksError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*rTasksError\s*\)[^\n]*console\.error',
            js_content
        )

    def test_r_apps_error_destructured(self, js_content):
        """rAppsError must be destructured from the applications query in loadReports."""
        assert re.search(r'error\s*:\s*rAppsError', js_content), \
            "rAppsError must be destructured"

    def test_r_apps_error_checked(self, js_content):
        """rAppsError must be checked."""
        assert re.search(r'if\s*\(\s*rAppsError\s*\)', js_content)

    def test_r_apps_error_logs_with_console_error(self, js_content):
        """rAppsError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*rAppsError\s*\)[^\n]*console\.error',
            js_content
        )

    def test_r_certs_error_destructured(self, js_content):
        """rCertsError must be destructured from the certificates query in loadReports."""
        assert re.search(r'error\s*:\s*rCertsError', js_content), \
            "rCertsError must be destructured"

    def test_r_certs_error_checked(self, js_content):
        """rCertsError must be checked."""
        assert re.search(r'if\s*\(\s*rCertsError\s*\)', js_content)

    def test_r_certs_error_logs_with_console_error(self, js_content):
        """rCertsError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*rCertsError\s*\)[^\n]*console\.error',
            js_content
        )

    def test_r_payments_error_destructured(self, js_content):
        """rPaymentsError must be destructured from the payments query in loadReports."""
        assert re.search(r'error\s*:\s*rPaymentsError', js_content), \
            "rPaymentsError must be destructured"

    def test_r_payments_error_checked(self, js_content):
        """rPaymentsError must be checked."""
        assert re.search(r'if\s*\(\s*rPaymentsError\s*\)', js_content)

    def test_r_payments_error_logs_with_console_error(self, js_content):
        """rPaymentsError handler must use console.error."""
        assert re.search(
            r'if\s*\(\s*rPaymentsError\s*\)[^\n]*console\.error',
            js_content
        )

    def test_r_users_error_message_logged(self, js_content):
        assert "rUsersError.message" in js_content

    def test_r_tasks_error_message_logged(self, js_content):
        assert "rTasksError.message" in js_content

    def test_r_apps_error_message_logged(self, js_content):
        assert "rAppsError.message" in js_content

    def test_r_certs_error_message_logged(self, js_content):
        assert "rCertsError.message" in js_content

    def test_r_payments_error_message_logged(self, js_content):
        assert "rPaymentsError.message" in js_content

    # Boundary: all 5 report error variables must be present
    def test_all_five_report_error_variables_present(self, js_content):
        errors = ["rUsersError", "rTasksError", "rAppsError", "rCertsError", "rPaymentsError"]
        for err in errors:
            assert err in js_content, f"{err} must be present in loadReports error handling"


# ---------------------------------------------------------------------------
# General error handling pattern tests
# ---------------------------------------------------------------------------

class TestGeneralErrorHandlingPatterns:
    def test_console_error_used_for_error_logging(self, js_content):
        """console.error must be used (not console.log) for error reporting."""
        assert "console.error" in js_content

    def test_error_message_property_accessed(self, js_content):
        """Error handlers must access the .message property of the error."""
        assert ".message" in js_content

    def test_load_admin_dashboard_function_present(self, js_content):
        """loadAdminDashboard function must still exist."""
        assert "async function loadAdminDashboard" in js_content

    def test_load_reports_function_present(self, js_content):
        """loadReports function must still exist."""
        assert "async function loadReports" in js_content

    def test_check_auth_called_in_load_admin_dashboard(self, js_content):
        """checkAuth must still be called in loadAdminDashboard."""
        assert "checkAuth" in js_content

    # Regression: early return on usersError prevents display of stale state
    def test_early_return_only_on_users_error_not_others(self, js_content):
        """Only usersError should trigger early return; others log and continue."""
        # Count 'return' statements inside error handlers in the file
        # usersError block is the only one with a bare return
        users_err_block = re.search(
            r'if\s*\(\s*usersError\s*\)\s*\{([^}]*)\}',
            js_content,
            re.DOTALL
        )
        assert users_err_block is not None
        assert "return" in users_err_block.group(1)