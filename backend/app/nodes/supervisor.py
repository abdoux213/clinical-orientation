from backend.app.state import MedicalState


def supervisor_node(state: MedicalState) -> dict:
    """Orchestre le workflow et décide de l'étape suivante."""
    messages = list(state.get("messages") or [])
    answers = state.get("patient_answers") or []
    diagnostic_summary = state.get("diagnostic_summary") or ""
    physician_treatment = state.get("physician_treatment") or ""
    final_report = state.get("final_report") or ""

    if len(answers) < 5 or not diagnostic_summary:
        next_step = "diagnostic_agent"
    elif not physician_treatment:
        next_step = "physician_review"
    elif not final_report:
        next_step = "report_agent"
    else:
        next_step = "FINISH"

    messages.append(
        {
            "role": "assistant",
            "content": f"[Supervisor] Prochaine étape : {next_step}",
        }
    )
    return {"next": next_step, "messages": messages}
