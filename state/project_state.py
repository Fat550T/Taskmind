from typing import TypedDict, Optional

class ProjectState(TypedDict):
    ticket_id: str
    ticket_ref: Optional[dict]
    repo_path: str
    _context: Optional[str]

    spec_doc_ref: Optional[str]
    specification_status: Optional[str]

    clarify_status: Optional[str]
    clarification_round: Optional[int]
    clarification_pending_question: Optional[str]
    clarification_log: Optional[list]
    _clarification_answer: Optional[str]

    plan_doc_ref: Optional[str]
    planning_status: Optional[str]

    analysis_status: Optional[str]
    analysis_report_ref: Optional[str]

    tasks_doc_ref: Optional[str]
    tasks_status: Optional[str]

    adr_ref: Optional[str]
    architecture_status: Optional[str]

    security_review_ref: Optional[str]
    security_status: Optional[str]

    implementation_status: Optional[str]
    _impl_round: Optional[int]
    _impl_stalled: Optional[int]

    # --- Unit Tests ---
    unit_tests_status: Optional[str]
    unit_tests_summary: Optional[dict]
    _unit_tests_stdout_tail: Optional[str]
    _unit_test_fix_round: Optional[int]

    # --- Code Review ---
    code_review_ref: Optional[str]
    code_review_status: Optional[str]   # "approved" | "changes_requested" | "failed"
    _code_review_feedback: Optional[str]
    _code_review_fix_round: Optional[int]
        # --- E2E ---
    e2e_tests_status: Optional[str]
    e2e_tests_summary: Optional[dict]
    e2e_review_ref: Optional[str]
    e2e_review_status: Optional[str]   # "approved" | "changes_requested" | "failed"
    _e2e_review_feedback: Optional[str]
    _e2e_review_fix_round: Optional[int]
        # --- Documentation ---
    documentation_ref: Optional[str]
    documentation_status: Optional[str]
    documentation_validation_ref: Optional[str]
    documentation_validation_status: Optional[str]
    _documentation_feedback: Optional[str]
    _documentation_fix_round: Optional[int]

    branch_name: Optional[str]
    pr_url: Optional[str]
    pr_status: Optional[str]