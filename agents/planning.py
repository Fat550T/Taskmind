from runtime.agent_runner import run_speckit_skill, find_latest_artifact


def planning_node(state):
    res = run_speckit_skill(state["repo_path"], "plan", state.get("_context", ""))
    doc_path = find_latest_artifact(state["repo_path"], "plan.md")
    success = res.get("success") and doc_path is not None

    print(f"[planning] {'OK' if success else 'FAILED'}" + (f" — {doc_path}" if doc_path else ""))
    if not success:
        print(f"  --- stdout ---\n{res.get('stdout', '')}")
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "planning_status": "ok" if success else "failed",
        "plan_doc_ref": doc_path,
    }