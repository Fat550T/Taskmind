import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact
from runtime.git_runner import get_diff

MAX_DIFF_CHARS = 20000


def code_review_node(state):
    diff_res = get_diff(state["repo_path"])
    diff_content = diff_res.get("stdout", "")[:MAX_DIFF_CHARS]

    adr_content = ""
    if state.get("adr_ref"):
        adr_content = pathlib.Path(state["adr_ref"]).read_text(encoding="utf-8")

    prompt = f"""Review the diff below against the ADR and general code quality/conventions.
Write the result at specs/<feature-dir>/code-review.md, including:
- a short summary of what changed
- issues found, grouped by severity (blocking / minor)
- a final verdict line: **Verdict**: Approved | ChangesRequested

ADR:
{adr_content}

Diff:
{diff_content}"""

    res = run_custom_prompt(state["repo_path"], prompt, timeout=1800)
    review_path = find_latest_artifact(state["repo_path"], "code-review.md")
    success = res.get("success") and review_path is not None

    verdict = "changes_requested"
    content = ""
    if review_path:
        content = pathlib.Path(review_path).read_text(encoding="utf-8")
        if "Verdict**: Approved" in content:
            verdict = "approved"

    print(f"[code_review] {'OK' if success else 'FAILED'} — verdict: {verdict}" + (f" — {review_path}" if review_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    if verdict == "approved":
        return {
            "code_review_ref": review_path,
            "code_review_status": "approved",
            "_code_review_feedback": None,
        }

    round_n = state.get("_code_review_fix_round", 0)
    return {
        "code_review_ref": review_path,
        "code_review_status": verdict if success else "failed",
        "_code_review_feedback": content[:6000] if content else None,
        "_code_review_fix_round": round_n + 1,
    }