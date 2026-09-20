from runtime.agent_runner import run_speckit_skill, find_latest_artifact


def specification_node(state):
    res = run_speckit_skill(state["repo_path"], "specify", state.get("_context", ""))
    doc_path = find_latest_artifact(state["repo_path"], "spec.md")
    success = res.get("success") and doc_path is not None

    print(f"[specification] {'OK' if success else 'FAILED'}" + (f" — {doc_path}" if doc_path else ""))
    if not success:
        print(f"  --- stdout ---\n{res.get('stdout', '')}")
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "specification_status": "ok" if success else "failed",
        "spec_doc_ref": doc_path,
    }