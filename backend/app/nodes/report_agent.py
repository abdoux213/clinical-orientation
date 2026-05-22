from langchain_core.messages import AIMessage

from backend.app.nodes.llm_utils import get_llm
from backend.app.state import MedicalState

DISCLAIMER = (
    "Ce système ne remplace pas une consultation médicale. "
    "Il s'agit d'un exercice académique d'orientation clinique préliminaire."
)


def _build_report(state: MedicalState) -> str:
    llm = get_llm()
    prompt = f"""Rédige un rapport final structuré (exercice académique) avec les sections :
1. Contexte patient
2. Synthèse clinique préliminaire
3. Recommandation intermédiaire
4. Avis du médecin traitant
5. Conclusion et mise en garde

Cas : {state.get('patient_case', '')}
Réponses : {state.get('patient_answers', [])}
Synthèse : {state.get('diagnostic_summary', '')}
Recommandation intermédiaire : {state.get('interim_care', '')}
Conduite médecin : {state.get('physician_treatment', '')}

Terminer par : "{DISCLAIMER}"
Ne pas poser de diagnostic définitif.
"""
    if llm:
        return llm.invoke(prompt).content

    return f"""# Rapport d'orientation clinique préliminaire

## 1. Contexte patient
{state.get('patient_case', 'N/A')}

## 2. Réponses patient (5 questions)
{chr(10).join(f'- {a}' for a in state.get('patient_answers', []))}

## 3. Synthèse clinique préliminaire
{state.get('diagnostic_summary', 'N/A')}

## 4. Recommandation intermédiaire
{state.get('interim_care', 'N/A')}

## 5. Conduite du médecin traitant
{state.get('physician_treatment', 'N/A')}

## 6. Conclusion
Orientation à titre informatif dans le cadre pédagogique.

**{DISCLAIMER}**
"""


def report_agent_node(state: MedicalState) -> dict:
    messages = list(state.get("messages") or [])
    final_report = state.get("final_report") or _build_report(state)
    messages.append(AIMessage(content=f"[Report Agent]\n\n{final_report}"))
    return {
        "messages": messages,
        "final_report": final_report,
        "next": "FINISH",
        "pending_interrupt": None,
    }
