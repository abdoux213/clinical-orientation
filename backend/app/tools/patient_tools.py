from langchain_core.tools import tool

QUESTION_BANK = [
    "Depuis combien de temps ressentez-vous ces symptômes ?",
    "Avez-vous de la fièvre ou des frissons ?",
    "La douleur ou l'inconfort s'aggrave-t-il à l'effort ou au repos ?",
    "Prenez-vous actuellement des médicaments ou avez-vous des allergies connues ?",
    "Avez-vous des antécédents médicaux importants (cardiaques, respiratoires, diabète) ?",
]


@tool
def ask_patient(question_index: int, patient_case: str) -> dict:
    """Pose une question au patient (index 0-4). Retourne la question formulée."""
    idx = max(0, min(int(question_index), len(QUESTION_BANK) - 1))
    question = QUESTION_BANK[idx]
    return {
        "question_index": idx,
        "question": question,
        "patient_case_context": patient_case[:500] if patient_case else "",
    }
