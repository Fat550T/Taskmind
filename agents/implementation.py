import pathlib
import re
from runtime.agent_runner import run_speckit_skill

MAX_IMPLEMENTATION_ROUNDS = 8
MAX_STALLED_ROUNDS = 2


def parse_tasks_checklist(tasks_path):
    content = pathlib.Path(tasks_path).read_text(encoding="utf-8")
    tasks = re.findall(r"^- \[([ xX])\]\s*(.+)$", content, re.MULTILINE)
    incomplete = [label for mark, label in tasks if mark.strip() == ""]
    return len(tasks), incomplete


def _build_feedback_context(state):
    parts = []
    if state.get("_unit_tests_stdout_tail"):
        parts.append(
            "--- Les tests unitaires ont échoué. Corrige le code en conséquence. ---\n"
            + state["_unit_tests_stdout_tail"]
        )
    if state.get("_code_review_feedback"):
        parts.append(
            "--- Le code review a demandé des changements. Corrige les points listés. ---\n"
            + state["_code_review_feedback"]
        )
    if state.get("_e2e_review_feedback"):
        parts.append(
            "--- La revue E2E a demandé des changements. Corrige les points listés. ---\n"
            + state["_e2e_review_feedback"]
        )
    return "\n\n".join(parts)


def implementation_node(state):
    tasks_path = state.get("tasks_doc_ref")
    total, incomplete_before = parse_tasks_checklist(tasks_path)

    round_n = state.get("_impl_round", 0) + 1
    print(f"[implementation] passage {round_n} — {total - len(incomplete_before)}/{total} tâches faites avant cet appel")

    context = state.get("_context", "") + "\n\n" + _build_feedback_context(state)

    res = run_speckit_skill(state["repo_path"], "implement", context, timeout=3600)
    if not res.get("success"):
        print(f"[implementation] appel en échec — {res.get('stderr', '')[:500]}")

    _, incomplete_after = parse_tasks_checklist(tasks_path)
    made_progress = len(incomplete_after) < len(incomplete_before)
    stalled = 0 if made_progress else state.get("_impl_stalled", 0) + 1

    # Une fois le round consommé, on efface les feedbacks pour ne pas les
    # réinjecter indéfiniment à chaque tour d'implémentation classique.
    cleared_feedback = {
        "_unit_tests_stdout_tail": None,
        "_code_review_feedback": None,
        "_e2e_review_feedback": None,
    }

    if not incomplete_after:
        print("[implementation] toutes les tâches sont complètes")
        return {
            "implementation_status": "ok", "_impl_round": round_n, "_impl_stalled": stalled,
            **cleared_feedback,
        }

    if stalled >= MAX_STALLED_ROUNDS or round_n >= MAX_IMPLEMENTATION_ROUNDS:
        print(f"[implementation] abandon — {len(incomplete_after)} tâche(s) restante(s), plus de progression")
        return {
            "implementation_status": "failed", "_impl_round": round_n, "_impl_stalled": stalled,
            **cleared_feedback,
        }

    print(f"[implementation] {len(incomplete_after)} tâche(s) restante(s) — on reboucle")
    return {
        "implementation_status": "in_progress", "_impl_round": round_n, "_impl_stalled": stalled,
        **cleared_feedback,
    }