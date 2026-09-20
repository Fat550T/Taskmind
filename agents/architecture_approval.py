from langgraph.types import interrupt


def architecture_approval_node(state):
    """Ne fait QUE attendre la décision humaine — pas d'effet de bord ici."""
    decision = interrupt({
        "message": "Valide l'ADR avant de continuer.",
        "adr_ref": state.get("adr_ref"),
    })
    status = "approved" if decision == "approved" else "changes_requested"
    print(f"[architecture_approval] décision reçue : {status}")
    return {"architecture_status": status}