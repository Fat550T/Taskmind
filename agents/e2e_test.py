from runtime.e2e_test_runner import run_e2e_tests


def e2e_test_node(state):
    res = run_e2e_tests(state["repo_path"])
    api_summary = res["api"]["summary"]
    ui_summary = res["ui"]["summary"]

    print(f"[e2e_test] API: {'OK' if res['api']['stdout'] and api_summary and api_summary['failures']==0 and api_summary['errors']==0 else 'FAILED'}"
          f" — {api_summary}")
    print(f"[e2e_test] UI:  {'OK' if res['ui']['stdout'] and ui_summary and ui_summary['failures']==0 and ui_summary['errors']==0 else 'FAILED'}"
          f" — {ui_summary}")

    if not res["success"]:
        print(f"  --- API stdout (tail) ---\n" + "\n".join(res["api"]["stdout"].splitlines()[-30:]))
        print(f"  --- UI stdout (tail) ---\n" + "\n".join(res["ui"]["stdout"].splitlines()[-30:]))

    return {
        "e2e_tests_status": "ok" if res["success"] else "failed",
        "e2e_tests_summary": {"api": api_summary, "ui": ui_summary},
    }