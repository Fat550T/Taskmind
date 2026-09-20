import subprocess
import re


def _run(repo_path: str, args: list[str], timeout: int = 120) -> dict:
    result = subprocess.run(
        args,
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
    }


def get_diff(repo_path: str) -> dict:
    """Diff des changements non commités (working tree vs dernier commit)."""
    return _run(repo_path, ["git", "diff", "HEAD"], timeout=60)


def ensure_branch(repo_path: str, branch_name: str) -> dict:
    check = _run(repo_path, ["git", "rev-parse", "--verify", branch_name])
    if check["success"]:
        return _run(repo_path, ["git", "checkout", branch_name])
    return _run(repo_path, ["git", "checkout", "-b", branch_name])


def commit_and_push(repo_path: str, branch_name: str, commit_message: str) -> dict:
    add_res = _run(repo_path, ["git", "add", "-A"])
    if not add_res["success"]:
        return add_res

    status_res = _run(repo_path, ["git", "status", "--porcelain"])
    if not status_res["stdout"].strip():
        return {"success": True, "stdout": "(rien à committer)", "stderr": ""}

    commit_res = _run(repo_path, ["git", "commit", "-m", commit_message])
    if not commit_res["success"]:
        return commit_res

    return _run(repo_path, ["git", "push", "-u", "origin", branch_name], timeout=300)


def create_or_update_pr(repo_path: str, branch_name: str, title: str, body: str, base: str) -> dict:
    existing = _run(repo_path, ["gh", "pr", "view", branch_name, "--json", "url"])
    if existing["success"]:
        match = re.search(r'"url"\s*:\s*"([^"]+)"', existing["stdout"])
        if match:
            return {"success": True, "pr_url": match.group(1), "created": False}

    create_res = _run(
        repo_path,
        ["gh", "pr", "create", "--head", branch_name, "--base", base, "--title", title, "--body", body],
        timeout=120,
    )
    if not create_res["success"]:
        return {"success": False, "pr_url": None, "stderr": create_res["stderr"]}

    url_match = re.search(r"https://\S+", create_res["stdout"])
    return {"success": True, "pr_url": url_match.group(0) if url_match else None, "created": True}