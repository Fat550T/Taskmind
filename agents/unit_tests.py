from runtime.unit_test_runner import run_unit_tests


def unit_tests_node(state):
    res = run_unit_tests(state["repo_path"])
    round_n = state.get("_unit_test_fix_round", 0)

    print(f"[unit_tests] {'OK' if res['success'] else 'FAILED'}" + (f" — {res['summary']}" if res.get('summary') else ""))
    if not res["success"]:
        print(f"  --- stdout (tail) ---\n" + "\n".join(res.get("stdout", "").splitlines()[-40:]))

    if res["success"]:
        return {
            "unit_tests_status": "ok",
            "unit_tests_summary": res.get("summary"),
            "_unit_tests_stdout_tail": None,
        }

    return {
        "unit_tests_status": "failed",
        "unit_tests_summary": res.get("summary"),
        "_unit_tests_stdout_tail": "\n".join(res.get("stdout", "").splitlines()[-60:]),
        "_unit_test_fix_round": round_n + 1,
    }