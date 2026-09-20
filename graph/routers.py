from langgraph.graph import END

MAX_UNIT_TEST_FIX_ROUNDS = 3
MAX_CODE_REVIEW_FIX_ROUNDS = 3
MAX_E2E_REVIEW_FIX_ROUNDS = 3
MAX_DOCUMENTATION_FIX_ROUNDS = 3


def make_router(status_key, next_node):
    def router(state):
        return next_node if state.get(status_key) == "ok" else END
    return router


def clarification_start_router(state):
    status = state.get("clarify_status")
    if status == "ok":
        return "planning"
    if status == "in_progress":
        return "clarification_ask"
    return END


def clarification_apply_router(state):
    status = state.get("clarify_status")
    if status == "ok":
        return "planning"
    if status == "in_progress":
        return "clarification_ask"
    return END


def architecture_review_router(state):
    return "architecture_approval" if state.get("architecture_status") == "pending" else END


def architecture_approval_router(state):
    return "security_review" if state.get("architecture_status") == "approved" else END


def security_review_router(state):
    return "security_approval" if state.get("security_status") == "pending" else END


def security_approval_router(state):
    return "implementation" if state.get("security_status") == "approved" else END


def implementation_router(state):
    status = state.get("implementation_status")
    if status == "in_progress":
        return "implementation"
    if status == "ok":
        return "unit_tests"
    return END


def unit_tests_router(state):
    if state.get("unit_tests_status") == "ok":
        return "code_review"
    if state.get("_unit_test_fix_round", 0) < MAX_UNIT_TEST_FIX_ROUNDS:
        return "implementation"
    return END


def code_review_router(state):
    if state.get("code_review_status") == "approved":
        return "e2e_test"
    if state.get("_code_review_fix_round", 0) < MAX_CODE_REVIEW_FIX_ROUNDS:
        return "implementation"
    return END


def e2e_test_router(state):
    return "e2e_review" if state.get("e2e_tests_status") == "ok" else END


def e2e_review_router(state):
    if state.get("e2e_review_status") == "approved":
        return "documentation"
    if state.get("_e2e_review_fix_round", 0) < MAX_E2E_REVIEW_FIX_ROUNDS:
        return "implementation"
    return END


def documentation_router(state):
    return "documentation_validation" if state.get("documentation_status") == "ok" else END


def documentation_validation_router(state):
    if state.get("documentation_validation_status") == "approved":
        return "pr_creation"
    if state.get("_documentation_fix_round", 0) < MAX_DOCUMENTATION_FIX_ROUNDS:
        return "documentation"
    return END