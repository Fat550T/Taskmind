import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact


def security_review_node(state):
    """Génère le rapport de sécurité (threat model + checklist) — effet de bord,
    ne doit PAS être rejoué au resume (même logique que architecture_review_node)."""
    adr_content = ""
    if state.get("adr_ref"):
        adr_content = pathlib.Path(state["adr_ref"]).read_text(encoding="utf-8")

    prompt = f"""Based on the ADR below and this feature's context, perform a security review.
Write the result at specs/<feature-dir>/security-review.md, covering:
- threat model summary (auth, injection, data exposure, access control)
- a security checklist with pass/fail per item
- a final verdict line: **Verdict**: Pass | Concerns | Fail

Context:
{state.get('_context', '')}

ADR:
{adr_content}"""

    res = run_custom_prompt(state["repo_path"], prompt)
    review_path = find_latest_artifact(state["repo_path"], "security-review.md")
    success = res.get("success") and review_path is not None

    print(f"[security_review] {'OK' if success else 'FAILED'}" + (f" — {review_path}" if review_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "security_review_ref": review_path,
        "security_status": "pending" if success else "failed",
    }