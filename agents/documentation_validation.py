import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact


def documentation_validation_node(state):
    """Vérifie la documentation générée par rapport au spec et aux critères d'acceptation
    (autonome — pas de gate humain)."""
    doc_content = ""
    if state.get("documentation_ref"):
        doc_content = pathlib.Path(state["documentation_ref"]).read_text(encoding="utf-8")

    prompt = f"""Review the documentation below against the feature's acceptance criteria.
Write the result at specs/<feature-dir>/documentation-review.md, including:
- whether every acceptance criterion is reflected in the documentation
- any missing configuration, endpoint, or error case
- a final verdict line: **Verdict**: Approved | ChangesRequested

Acceptance criteria context:
{state.get('_context', '')}

Documentation:
{doc_content}"""

    res = run_custom_prompt(state["repo_path"], prompt, timeout=1800)
    review_path = find_latest_artifact(state["repo_path"], "documentation-review.md")
    success = res.get("success") and review_path is not None

    verdict = "changes_requested"
    content = ""
    if review_path:
        content = pathlib.Path(review_path).read_text(encoding="utf-8")
        if "Verdict**: Approved" in content:
            verdict = "approved"

    print(f"[documentation_validation] {'OK' if success else 'FAILED'} — verdict: {verdict}" + (f" — {review_path}" if review_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    if verdict == "approved":
        return {
            "documentation_validation_ref": review_path,
            "documentation_validation_status": "approved",
            "_documentation_feedback": None,
        }

    round_n = state.get("_documentation_fix_round", 0)
    return {
        "documentation_validation_ref": review_path,
        "documentation_validation_status": verdict if success else "failed",
        "_documentation_feedback": content[:6000] if content else None,
        "_documentation_fix_round": round_n + 1,
    }