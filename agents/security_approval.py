from langgraph.types import interrupt


def security_approval_node(state):
    """Ne fait QUE attendre la décision humaine — pas d'effet de bord ici."""
    decision = interrupt({
        "message": "Valide le security review avant de continuer.",
        "security_review_ref": state.get("security_review_ref"),
    })
    status = "approved" if decision == "approved" else "blocked"
    print(f"[security_approval] décision reçue : {status}")
    return {"security_status": status}