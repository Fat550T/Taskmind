from mcp.atlassian import fetch_jira_ticket


def extraction_node(state):
    ticket_ref = fetch_jira_ticket(state["ticket_id"])
    print(f"[extraction] OK — {ticket_ref.get('key')} - {ticket_ref.get('summary')}")

    context = f"""ID: {ticket_ref.get('key', '')}
Title: {ticket_ref.get('summary', '')}

Background: {ticket_ref.get('background', '')}

Scope:
{chr(10).join('- ' + s for s in ticket_ref.get('scope', []))}

Acceptance Criteria:
{chr(10).join('- ' + a for a in ticket_ref.get('acceptanceCriteria', []))}"""

    return {"ticket_ref": ticket_ref, "_context": context}