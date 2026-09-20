import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()


def _adf_to_text(node) -> str:
    """Convertit un document Atlassian Document Format (ADF) en texte markdown simplifié."""
    if not node:
        return ""
    lines = []

    def walk_inline(n):
        if n.get("type") == "text":
            return n.get("text", "")
        return "".join(walk_inline(c) for c in n.get("content", []))

    def walk(n):
        t = n.get("type")
        if t == "heading":
            level = n.get("attrs", {}).get("level", 3)
            text = "".join(walk_inline(c) for c in n.get("content", []))
            lines.append(f"{'#' * level} {text}")
        elif t == "paragraph":
            text = "".join(walk_inline(c) for c in n.get("content", []))
            if text.strip():
                lines.append(text)
        elif t == "bulletList":
            for item in n.get("content", []):
                item_text = "".join(
                    walk_inline(c) for sub in item.get("content", []) for c in sub.get("content", [])
                )
                lines.append(f"* {item_text}")
        elif t == "doc":
            for c in n.get("content", []):
                walk(c)
        else:
            for c in n.get("content", []):
                walk(c)

    walk(node)
    return "\n".join(lines)


def _parse_sections(description_text: str) -> dict:
    keywords = {"background", "scope", "acceptance criteria"}
    stop_keywords = {"out of scope"}
    buffer = {"pre": []}
    current = "pre"

    for line in description_text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if not stripped:
            continue
        low = stripped.lower()
        if low in keywords:
            current = low.replace(" ", "_")
            buffer[current] = []
            continue
        if low in stop_keywords:
            current = None
            continue
        if current is None:
            continue
        buffer.setdefault(current, []).append(stripped.lstrip("*").strip())

    return {
        "background": " ".join(buffer.get("background", buffer.get("pre", []))).strip(),
        "scope": buffer.get("scope", []),
        "acceptanceCriteria": buffer.get("acceptance_criteria", []),
    }


def fetch_jira_ticket(ticket_id: str) -> dict:
    email = os.environ["JIRA_EMAIL"]
    token = os.environ["JIRA_API_TOKEN"]
    base_url = os.environ["JIRA_BASE_URL"]

    url = f"{base_url}/rest/api/3/issue/{ticket_id}"
    response = requests.get(url, auth=(email, token))
    response.raise_for_status()
    data = response.json()
    fields = data.get("fields", {})

    description_text = _adf_to_text(fields.get("description"))
    sections = _parse_sections(description_text)

    assignee = fields.get("assignee")
    reporter = fields.get("reporter") or {}

    return {
        "key": data.get("key"),
        "summary": fields.get("summary"),
        "issueType": (fields.get("issuetype") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "project": {
            "key": (fields.get("project") or {}).get("key"),
            "name": (fields.get("project") or {}).get("name"),
        },
        "status": (fields.get("status") or {}).get("name"),
        "reporter": {"name": reporter.get("displayName"), "accountId": reporter.get("accountId")},
        "assignee": {"name": assignee.get("displayName"), "accountId": assignee.get("accountId")} if assignee else None,
        "labels": fields.get("labels", []),
        "components": [c.get("name") for c in fields.get("components", [])],
        "created": fields.get("created"),
        "updated": fields.get("updated"),
        "descriptionRaw": description_text,
        "background": sections["background"],
        "scope": sections["scope"],
        "acceptanceCriteria": sections["acceptanceCriteria"],
        "comments": [
            {
                "author": (c.get("author") or {}).get("displayName"),
                "body": _adf_to_text(c.get("body")) if isinstance(c.get("body"), dict) else c.get("body"),
                "created": c.get("created"),
            }
            for c in (fields.get("comment") or {}).get("comments", [])
        ],
    }
if __name__ == "__main__":
    import sys
    import json

    ticket_id = sys.argv[1]
    result = fetch_jira_ticket(ticket_id)
    print(json.dumps(result, ensure_ascii=False))