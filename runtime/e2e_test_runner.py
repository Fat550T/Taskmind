import subprocess
import re

SUREFIRE_SUMMARY_RE = re.compile(
    r"Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)"
)


def _parse_surefire_summary(stdout: str):
    matches = SUREFIRE_SUMMARY_RE.findall(stdout)
    if not matches:
        return None
    run, failures, errors, skipped = (int(x) for x in matches[-1])
    return {"run": run, "failures": failures, "errors": errors, "skipped": skipped}


def _run_suite(repo_path: str, service: str, timeout: int = 900) -> dict:
    result = subprocess.run(
        ["docker", "compose", "run", "--rm", "-T", service],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    summary = _parse_surefire_summary(result.stdout)
    tests_ok = summary is not None and summary["failures"] == 0 and summary["errors"] == 0
    return {
        "success": result.returncode == 0 and tests_ok,
        "summary": summary,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_e2e_tests(repo_path: str) -> dict:
    """Lance les suites API et UI (Playwright/Cucumber) via docker compose."""
    api_res = _run_suite(repo_path, "api-automation-testing")
    ui_res = _run_suite(repo_path, "ui-automation-testing")

    return {
        "success": api_res["success"] and ui_res["success"],
        "api": {"summary": api_res["summary"], "stdout": api_res["stdout"], "stderr": api_res["stderr"]},
        "ui": {"summary": ui_res["summary"], "stdout": ui_res["stdout"], "stderr": ui_res["stderr"]},
    }