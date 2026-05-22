from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from backend.app.state import MedicalState


def physician_review_node(state: MedicalState) -> dict:
    """Human-in-the-loop : le médecin valide et propose une conduite à tenir."""
    messages = list(state.get("messages") or [])
    summary = state.get("diagnostic_summary") or ""
    interim = state.get("interim_care") or ""
    treatment = state.get("physician_treatment") or ""

    if not treatment:
        payload = interrupt(
            {
                "type": "physician_review",
                "diagnostic_summary": summary,
                "interim_care": interim,
                "message": (
                    "Le médecin traitant reçoit la synthèse et la recommandation intermédiaire. "
                    "Proposer un traitement ou une conduite à tenir."
                ),
            }
        )
        if isinstance(payload, dict):
            treatment = payload.get("physician_treatment") or payload.get("treatment") or str(payload)
        else:
            treatment = str(payload)

    messages.append(
        AIMessage(content=f"[Physician Review] Conduite retenue : {treatment}")
    )
    return {
        "messages": messages,
        "physician_treatment": treatment,
        "next": "report_agent",
    }
