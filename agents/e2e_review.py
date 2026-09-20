import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact


def e2e_review_node(state):
    summary = state.get("e2e_tests_summary", {})

    prompt = f"""Review the end-to-end test results below (API + UI suites) against the spec's
acceptance criteria. Write the result at specs/<feature-dir>/e2e-review.md, including:
- a short summary of coverage vs acceptance criteria
- any gaps or flaky-looking failures worth flagging
- a final verdict line: **Verdict**: Approved | ChangesRequested

Acceptance criteria context:
{state.get('_context', '')}

E2E summary:
{summary}"""

    res = run_custom_prompt(state["repo_path"], prompt, timeout=1800)
    review_path = find_latest_artifact(state["repo_path"], "e2e-review.md")
    success = res.get("success") and review_path is not None

    verdict = "changes_requested"
    content = ""
    if review_path:
        content = pathlib.Path(review_path).read_text(encoding="utf-8")
        if "Verdict**: Approved" in content:
            verdict = "approved"

    print(f"[e2e_review] {'OK' if success else 'FAILED'} — verdict: {verdict}" + (f" — {review_path}" if review_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    if verdict == "approved":
        return {
            "e2e_review_ref": review_path,
            "e2e_review_status": "approved",
            "_e2e_review_feedback": None,
        }

    round_n = state.get("_e2e_review_fix_round", 0)
    return {
        "e2e_review_ref": review_path,
        "e2e_review_status": verdict if success else "failed",
        "_e2e_review_feedback": content[:6000] if content else None,
        "_e2e_review_fix_round": round_n + 1,
    }