import re
from runtime.git_runner import ensure_branch, commit_and_push, create_or_update_pr

BASE_BRANCH = "appmod/java-upgrade-20260801203757"  # à confirmer/ajuster


def _slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:40]


def pr_creation_node(state):
    ticket_id = state["ticket_id"]
    summary = (state.get("ticket_ref") or {}).get("summary", "")
    branch_name = f"feature/{ticket_id.lower()}-{_slugify(summary)}"

    branch_res = ensure_branch(state["repo_path"], branch_name)
    if not branch_res["success"]:
        print(f"[pr_creation] échec checkout/création branche — {branch_res['stderr'][:300]}")
        return {"pr_status": "failed"}

    commit_message = f"{ticket_id}: {summary}"
    push_res = commit_and_push(state["repo_path"], branch_name, commit_message)
    if not push_res["success"]:
        print(f"[pr_creation] échec commit/push — {push_res['stderr'][:300]}")
        return {"pr_status": "failed", "branch_name": branch_name}

    pr_title = f"{ticket_id}: {summary}"
    pr_body = (
        f"PR générée automatiquement par le pipeline TaskMind pour {ticket_id}.\n\n"
        f"- Spec: `{state.get('spec_doc_ref')}`\n"
        f"- Plan: `{state.get('plan_doc_ref')}`\n"
        f"- Tasks: `{state.get('tasks_doc_ref')}`\n"
        f"- ADR: `{state.get('adr_ref')}`\n"
        f"- Security review: `{state.get('security_review_ref')}`\n"
        f"- Code review: `{state.get('code_review_ref')}`\n"
        f"- E2E review: `{state.get('e2e_review_ref')}`\n"
        f"- Documentation: `{state.get('documentation_ref')}`\n"
    )
    pr_res = create_or_update_pr(state["repo_path"], branch_name, pr_title, pr_body, base=BASE_BRANCH)
    if not pr_res["success"]:
        print(f"[pr_creation] échec création PR — {pr_res.get('stderr', '')[:300]}")
        return {"pr_status": "failed", "branch_name": branch_name}

    print(f"[pr_creation] OK — {pr_res['pr_url']}")
    return {
        "pr_status": "ok",
        "branch_name": branch_name,
        "pr_url": pr_res["pr_url"],
    }