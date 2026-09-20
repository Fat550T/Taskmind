import pathlib
from runtime.agent_runner import run_speckit_skill


def analysis_node(state):
    """speckit.analyze — s'exécute après tasks.md ; vérifie aussi implicitement
    l'existence de spec/plan/tasks (remplace le persistence_check séparé)."""
    res = run_speckit_skill(state["repo_path"], "analyze", state.get("_context", ""))
    success = res.get("success", False)

    analysis_ref = None
    if success and state.get("tasks_doc_ref"):
        feature_dir = pathlib.Path(state["tasks_doc_ref"]).parent
        analysis_path = feature_dir / "analysis-report.md"
        analysis_path.write_text(res.get("stdout", ""), encoding="utf-8")
        analysis_ref = str(analysis_path)

    print(f"[analysis] {'OK' if success else 'FAILED'}" + (f" — {analysis_ref}" if analysis_ref else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "analysis_status": "ok" if success else "failed",
        "analysis_report_ref": analysis_ref,
    }