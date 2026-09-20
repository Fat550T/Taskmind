import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact


def architecture_review_node(state):
    """Génère l'ADR (effet de bord — ne doit PAS être rejoué au resume)."""
    analysis_content = ""
    if state.get("analysis_report_ref"):
        analysis_content = pathlib.Path(state["analysis_report_ref"]).read_text(encoding="utf-8")

    prompt = f"""Based on plan.md, tasks.md, and the cross-artifact analysis below for this feature,
write an Architecture Decision Record (ADR) at specs/<feature-dir>/adr.md.
Summarize key architectural decisions, trade-offs, and risks for this change.
The file MUST start with exactly this line: **Status**: Proposed

Context:
{state.get('_context', '')}

Cross-Artifact Analysis:
{analysis_content}"""

    res = run_custom_prompt(state["repo_path"], prompt)
    adr_path = find_latest_artifact(state["repo_path"], "adr.md")
    success = res.get("success") and adr_path is not None

    print(f"[architecture_review] {'OK' if success else 'FAILED'}" + (f" — {adr_path}" if adr_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {"adr_ref": adr_path, "architecture_status": "pending" if success else "failed"}