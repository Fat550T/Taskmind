from langgraph.graph import StateGraph, END
from state.project_state import ProjectState

from agents.extraction import extraction_node
from agents.specification import specification_node
from agents.clarification import (
    clarification_start_node,
    clarification_ask_node,
    clarification_apply_node,
)
from agents.planning import planning_node
from agents.tasks import tasks_node
from agents.analysis import analysis_node
from agents.architecture_review import architecture_review_node
from agents.architecture_approval import architecture_approval_node
from agents.security_review import security_review_node
from agents.security_approval import security_approval_node
from agents.implementation import implementation_node
from agents.unit_tests import unit_tests_node
from agents.code_review import code_review_node
from agents.e2e_test import e2e_test_node
from agents.e2e_review import e2e_review_node
from agents.documentation import documentation_node
from agents.documentation_validation import documentation_validation_node
from agents.pr_creation import pr_creation_node
from graph.routers import (
    make_router,
    clarification_start_router,
    clarification_apply_router,
    architecture_review_router,
    architecture_approval_router,
    security_review_router,
    security_approval_router,
    implementation_router,
    unit_tests_router,
    code_review_router,
    e2e_test_router,
    e2e_review_router,
    documentation_router,
    documentation_validation_router,
)


def build_graph(checkpointer=None):
    g = StateGraph(ProjectState)

    g.add_node("extraction", extraction_node)
    g.add_node("specification", specification_node)
    g.add_node("clarification_start", clarification_start_node)
    g.add_node("clarification_ask", clarification_ask_node)
    g.add_node("clarification_apply", clarification_apply_node)
    g.add_node("planning", planning_node)
    g.add_node("tasks", tasks_node)
    g.add_node("analysis", analysis_node)
    g.add_node("architecture_review", architecture_review_node)
    g.add_node("architecture_approval", architecture_approval_node)
    g.add_node("security_review", security_review_node)
    g.add_node("security_approval", security_approval_node)
    g.add_node("implementation", implementation_node)
    g.add_node("unit_tests", unit_tests_node)
    g.add_node("code_review", code_review_node)
    g.add_node("e2e_test", e2e_test_node)
    g.add_node("e2e_review", e2e_review_node)
    g.add_node("documentation", documentation_node)
    g.add_node("documentation_validation", documentation_validation_node)
    g.add_node("pr_creation", pr_creation_node)
    g.set_entry_point("extraction")
    g.add_edge("extraction", "specification")

    g.add_conditional_edges(
        "specification",
        make_router("specification_status", "clarification_start"),
        {"clarification_start": "clarification_start", END: END},
    )
    g.add_conditional_edges(
        "clarification_start",
        clarification_start_router,
        {"planning": "planning", "clarification_ask": "clarification_ask", END: END},
    )
    g.add_edge("clarification_ask", "clarification_apply")
    g.add_conditional_edges(
        "clarification_apply",
        clarification_apply_router,
        {"planning": "planning", "clarification_ask": "clarification_ask", END: END},
    )
    g.add_conditional_edges(
        "planning", make_router("planning_status", "tasks"), {"tasks": "tasks", END: END}
    )
    g.add_conditional_edges(
        "tasks", make_router("tasks_status", "analysis"), {"analysis": "analysis", END: END}
    )
    g.add_conditional_edges(
        "analysis",
        make_router("analysis_status", "architecture_review"),
        {"architecture_review": "architecture_review", END: END},
    )
    g.add_conditional_edges(
        "architecture_review",
        architecture_review_router,
        {"architecture_approval": "architecture_approval", END: END},
    )
    g.add_conditional_edges(
        "architecture_approval",
        architecture_approval_router,
        {"security_review": "security_review", END: END},
    )
    g.add_conditional_edges(
        "security_review",
        security_review_router,
        {"security_approval": "security_approval", END: END},
    )
    g.add_conditional_edges(
        "security_approval",
        security_approval_router,
        {"implementation": "implementation", END: END},
    )
    g.add_conditional_edges(
        "implementation",
        implementation_router,
        {"implementation": "implementation", "unit_tests": "unit_tests", END: END},
    )
    g.add_conditional_edges(
        "unit_tests",
        unit_tests_router,
        {"code_review": "code_review", "implementation": "implementation", END: END},
    )
    g.add_conditional_edges(
        "code_review",
        code_review_router,
        {"e2e_test": "e2e_test", "implementation": "implementation", END: END},
    )
    g.add_conditional_edges(
        "e2e_test",
        e2e_test_router,
        {"e2e_review": "e2e_review", END: END},
    )
    g.add_conditional_edges(
        "e2e_review",
        e2e_review_router,
        {"documentation": "documentation", "implementation": "implementation", END: END},
    )
    g.add_conditional_edges(
        "documentation",
        documentation_router,
        {"documentation_validation": "documentation_validation", END: END},
    )
    
    g.add_conditional_edges(
    "documentation_validation",
    documentation_validation_router,
    {"documentation": "documentation", "pr_creation": "pr_creation", END: END},
    )
    g.add_edge("pr_creation", END)
    return g.compile(checkpointer=checkpointer)