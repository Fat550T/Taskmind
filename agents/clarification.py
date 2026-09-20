import pathlib
import re
from langgraph.types import interrupt
from runtime.agent_runner import run_speckit_skill, resume_codex_skill

MAX_CLARIFICATION_ROUNDS = 6
MARKER_RE = re.compile(r"\[NEEDS CLARIFICATION[^\]]*\]")


def _pending_markers(spec_path):
    """Vérité terrain pour savoir si clarify est terminé : on relit spec.md
    plutôt que de faire confiance à ce que Codex prétend."""
    if not spec_path or not pathlib.Path(spec_path).exists():
        return []
    content = pathlib.Path(spec_path).read_text(encoding="utf-8")
    return MARKER_RE.findall(content)


def _extract_question(stdout: str) -> str:
    """Heuristique simple : on relaie la fin du stdout de Codex comme 'question'.
    À AJUSTER une fois que tu as vu le format réel de sortie de speckit.clarify
    (ex: s'il préfixe par 'Q1:', on peut le parser plus précisément)."""
    lines = [l for l in stdout.strip().splitlines() if l.strip()]
    return "\n".join(lines[-15:]) if lines else "(pas de question détectée dans la sortie Codex)"


def clarification_start_node(state):
    """Premier appel à speckit.clarify (effet de bord — pas rejouable)."""
    res = run_speckit_skill(state["repo_path"], "clarify", state.get("_context", ""))
    if not res.get("success"):
        print(f"[clarification] appel initial en échec — {res.get('stderr', '')[:300]}")
        return {"clarify_status": "failed"}

    remaining = _pending_markers(state.get("spec_doc_ref"))
    print(f"[clarification] démarrage — {len(remaining)} marqueur(s) détecté(s)")

    if not remaining:
        return {"clarify_status": "ok", "clarification_round": 0, "clarification_log": []}

    return {
        "clarify_status": "in_progress",
        "clarification_round": 0,
        "clarification_log": [],
        "clarification_pending_question": _extract_question(res.get("stdout", "")),
    }


def clarification_ask_node(state):
    """Sans effet de bord — rejouable sans risque au resume : expose la question
    en attente et suspend le graphe (même pattern que architecture_approval_node)."""
    question = state.get("clarification_pending_question", "(question manquante)")
    round_n = state.get("clarification_round", 0)
    print(f"[clarification] round {round_n} — en attente d'une réponse humaine")

    answer = interrupt({
        "message": "SpecKit clarify attend une réponse.",
        "question": question,
        "round": round_n,
    })
    return {"_clarification_answer": answer}


def clarification_apply_node(state):
    """Avec effet de bord — envoie la réponse à Codex via resume, revérifie spec.md."""
    round_n = state.get("clarification_round", 0) + 1
    answer = state.get("_clarification_answer", "")
    log = list(state.get("clarification_log", []))

    res = resume_codex_skill(state["repo_path"], answer)
    if not res.get("success"):
        print(f"[clarification] resume en échec — {res.get('stderr', '')[:300]}")
        return {"clarify_status": "failed", "clarification_round": round_n}

    log.append({"question": state.get("clarification_pending_question"), "answer": answer})
    remaining = _pending_markers(state.get("spec_doc_ref"))
    print(f"[clarification] round {round_n} — {len(remaining)} marqueur(s) restant(s)")

    if not remaining or round_n >= MAX_CLARIFICATION_ROUNDS:
        if remaining:
            print(f"[clarification] abandon — limite de {MAX_CLARIFICATION_ROUNDS} rounds atteinte")
        return {
            "clarify_status": "ok" if not remaining else "failed",
            "clarification_log": log,
            "clarification_round": round_n,
            "clarification_pending_question": None,
        }

    return {
        "clarify_status": "in_progress",
        "clarification_log": log,
        "clarification_round": round_n,
        "clarification_pending_question": _extract_question(res.get("stdout", "")),
    }