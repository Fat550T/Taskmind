from runtime.agent_runner import run_speckit_skill, find_latest_artifact


def tasks_node(state):
    res = run_speckit_skill(state["repo_path"], "tasks", state.get("_context", ""))
    doc_path = find_latest_artifact(state["repo_path"], "tasks.md")
    success = res.get("success") and doc_path is not None

    print(f"[tasks] {'OK' if success else 'FAILED'}" + (f" — {doc_path}" if doc_path else ""))
    if not success:
        print(f"  --- stdout ---\n{res.get('stdout', '')}")
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "tasks_status": "ok" if success else "failed",
        "tasks_doc_ref": doc_path,
    }