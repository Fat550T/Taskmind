import subprocess
import pathlib
import os
import tempfile
from dotenv import load_dotenv

load_dotenv()


def run_speckit_skill(repo_path: str, skill_name: str, ticket_context: str = "", timeout: int = 1800) -> dict:
    """Invoque un skill SpecKit via Codex (ex: skill_name='specify' -> $speckit-specify).
    Ne réimplémente rien : envoie juste l'invocation du skill + le contexte du ticket à Codex."""
    prompt = f"$speckit-{skill_name}\n\n{ticket_context}".strip()
    return _run_codex(repo_path, prompt, timeout=timeout)


def run_custom_prompt(repo_path: str, prompt: str, timeout: int = 1800) -> dict:
    """Comme run_speckit_skill, mais pour un prompt libre (pas de préfixe $speckit-)."""
    return _run_codex(repo_path, prompt.strip(), timeout=timeout)


def _run_codex(repo_path: str, prompt: str, timeout: int = 1800) -> dict:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write(prompt)
    tmp.close()
    tmp_path = tmp.name

    ps_script = (
        f"Get-Content -Raw -LiteralPath '{tmp_path}' | "
        f"codex exec - --sandbox workspace-write --skip-git-repo-check"
    )

    env = os.environ.copy()

    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        # Sur Windows, exc.stdout/exc.stderr contiennent souvent ce que Codex avait
        # déjà produit avant le kill du process — on les récupère plutôt que de
        # laisser l'exception remonter et planter tout le graphe LangGraph.
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\n[TIMEOUT] Codex n'a pas répondu en {timeout}s."
        return {"success": False, "stdout": stdout, "stderr": stderr}
    finally:
        os.unlink(tmp_path)

    stderr = result.stderr or ""
    stdout = result.stdout or ""
    real_success = result.returncode == 0

    return {"success": real_success, "stdout": stdout, "stderr": stderr}


def find_latest_artifact(repo_path: str, filename: str):
    """Cherche le fichier `filename` le plus récent sous specs/, peu importe le sous-dossier."""
    specs_dir = pathlib.Path(repo_path) / "specs"
    if not specs_dir.exists():
        return None
    matches = list(specs_dir.rglob(filename))
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(matches[0])


def resume_codex_skill(repo_path: str, answer_text: str, timeout: int = 1800) -> dict:
    """Poursuit la DERNIÈRE session Codex de ce repo_path pour continuer la
    conversation de clarify. --last est scopé au répertoire courant : ne fonctionne
    correctement que si aucun autre appel Codex n'a eu lieu dans ce repo_path entre
    les deux tours. À vérifier avec `codex exec resume --help` sur ta version —
    le flag exact (--last vs un session-id explicite à capturer depuis le 1er appel)
    peut différer selon la version de Codex CLI installée."""
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    tmp.write(answer_text.strip())
    tmp.close()
    tmp_path = tmp.name

    ps_script = (
        f"$answer = Get-Content -Raw -LiteralPath '{tmp_path}'; "
        f"codex exec resume --last \"$answer\" --sandbox workspace-write --skip-git-repo-check"
    )
    env = os.environ.copy()

    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = (exc.stderr or "") + f"\n[TIMEOUT] Codex n'a pas répondu en {timeout}s."
        return {"success": False, "stdout": stdout, "stderr": stderr}
    finally:
        os.unlink(tmp_path)

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
    }