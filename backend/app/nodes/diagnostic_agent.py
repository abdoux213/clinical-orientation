from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from backend.app.nodes.llm_utils import get_llm
from backend.app.state import MedicalState
from backend.app.tools.care_tools import recommend_interim_care
from backend.app.tools.mcp_client import enrich_summary_with_mcp
from backend.app.tools.patient_tools import ask_patient


def _build_preliminary_summary(patient_case: str, answers: list[str], mcp_info: dict) -> str:
    llm = get_llm()
    answers_text = "\n".join(f"- Q{i + 1}: {a}" for i, a in enumerate(answers))
    red_flags = mcp_info.get("red_flags") or []
    guidance = mcp_info.get("guidance") or []
    prompt = f"""Tu es un assistant d'orientation clinique préliminaire (exercice académique).
Ne pose PAS de diagnostic définitif. Produis une synthèse clinique préliminaire courte.

Cas initial patient :
{patient_case}

Réponses collectées :
{answers_text}

Éléments MCP (fiche {mcp_info.get('category')}):
- Guidance: {guidance}
- Signes d'alerte à mentionner si pertinent: {red_flags}

Rédige 4-6 phrases : symptômes rapportés, éléments saillants, orientation préliminaire prudente.
Utilise les termes : orientation clinique préliminaire, synthèse clinique.
"""
    if llm:
        return llm.invoke(prompt).content
    return (
        "Synthèse clinique préliminaire : le patient décrit "
        f"{patient_case[:200]}. Les réponses aux 5 questions confirment un tableau "
        "à préciser en consultation. Orientation clinique préliminaire : surveillance "
        "et avis médical si aggravation. (Mode démo sans clé API LLM.)"
    )


def diagnostic_agent_node(state: MedicalState) -> dict:
    """Pose 5 questions via ask_patient (interrupt) puis synthèse + recommandation intermédiaire."""
    messages = list(state.get("messages") or [])
    patient_case = state.get("patient_case") or ""
    answers = list(state.get("patient_answers") or [])
    diagnostic_summary = state.get("diagnostic_summary") or ""

    if len(answers) < 5:
        idx = len(answers)
        tool_result = ask_patient.invoke({"question_index": idx, "patient_case": patient_case})
        question = tool_result["question"]
        answer = interrupt(
            {
                "type": "patient_question",
                "question_index": idx,
                "question": question,
            }
        )
        answers.append(str(answer))
        messages.append(AIMessage(content=f"[Diagnostic Agent] Q{idx + 1}: {question}"))
        messages.append(AIMessage(content=f"[Patient] {answer}"))
        return {
            "messages": messages,
            "patient_answers": answers,
            "question_count": len(answers),
            "current_question": question,
            "next": "diagnostic_agent",
        }

    if not diagnostic_summary:
        mcp_info = enrich_summary_with_mcp(patient_case, answers)
        diagnostic_summary = _build_preliminary_summary(patient_case, answers, mcp_info)
        red_flags = bool(mcp_info.get("red_flags")) or any(
            w in " ".join(answers).lower()
            for w in ("essoufflement", "douleur thoracique", "saignement", "perte de connaissance")
        )
        interim = recommend_interim_care.invoke(
            {
                "diagnostic_summary": diagnostic_summary,
                "answers_summary": " | ".join(answers),
                "red_flags": red_flags,
            }
        )
        messages.append(
            AIMessage(
                content=(
                    f"[Diagnostic Agent] Synthèse : {diagnostic_summary}\n\n"
                    f"Recommandation intermédiaire : {interim}"
                )
            )
        )
        return {
            "messages": messages,
            "diagnostic_summary": diagnostic_summary,
            "interim_care": interim,
            "next": "physician_review",
        }

    return {"next": "physician_review"}
