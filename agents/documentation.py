import pathlib
from runtime.agent_runner import run_custom_prompt, find_latest_artifact


def documentation_node(state):
    """Génère la documentation de la fonctionnalité (effet de bord — pas de gate humain)."""
    spec_content = ""
    if state.get("spec_doc_ref"):
        spec_content = pathlib.Path(state["spec_doc_ref"]).read_text(encoding="utf-8")

    adr_content = ""
    if state.get("adr_ref"):
        adr_content = pathlib.Path(state["adr_ref"]).read_text(encoding="utf-8")

    feedback = state.get("_documentation_feedback")
    feedback_block = ""
    if feedback:
        feedback_block = (
            "\n\nLa documentation précédente a été refusée avec les retours suivants. "
            f"Corrige-les :\n{feedback}"
        )

    prompt = f"""Based on the spec and ADR below, write user-facing and technical documentation
for this feature at specs/<feature-dir>/documentation.md, including:
- a short feature overview (what it does, for whom)
- the API contract (endpoints, request/response shapes, error codes) if applicable
- any configuration or operational notes (env vars, scheduler intervals, etc.)
- a short "how to verify" section referencing acceptance criteria

Also update the OpenAPI/Swagger annotations in the relevant controllers if they are
missing or incomplete, and update specs/<feature-dir>/quickstart.md if it already exists.

Spec:
{spec_content}

ADR:
{adr_content}{feedback_block}"""

    res = run_custom_prompt(state["repo_path"], prompt, timeout=1800)
    doc_path = find_latest_artifact(state["repo_path"], "documentation.md")
    success = res.get("success") and doc_path is not None

    print(f"[documentation] {'OK' if success else 'FAILED'}" + (f" — {doc_path}" if doc_path else ""))
    if not success:
        print(f"  --- stderr ---\n{res.get('stderr', '')}")

    return {
        "documentation_ref": doc_path,
        "documentation_status": "ok" if success else "failed",
    }