import subprocess
import pathlib
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


def run_unit_tests(repo_path: str, backend_subdir: str = "spring-publisher-service") -> dict:
    backend_path = pathlib.Path(repo_path) / backend_subdir

    if not (backend_path / "pom.xml").exists():
        return {"success": False, "summary": None, "error": f"pom.xml introuvable dans {backend_path}"}

    result = subprocess.run(
        "mvn test -B",
        cwd=str(backend_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
        shell=True,
    )

    summary = _parse_surefire_summary(result.stdout)
    process_ok = result.returncode == 0
    tests_ok = summary is not None and summary["failures"] == 0 and summary["errors"] == 0

    return {
        "success": process_ok and tests_ok,
        "summary": summary,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


if __name__ == "__main__":
    import sys, json

    repo_path = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/torch/taskmind-project/publisher-appTest"
    res = run_unit_tests(repo_path)
    print(json.dumps({k: v for k, v in res.items() if k not in ("stdout", "stderr")}, indent=2, ensure_ascii=False))
    if not res["success"]:
        print("--- stdout (tail) ---")
        print("\n".join(res.get("stdout", "").splitlines()[-40:]))