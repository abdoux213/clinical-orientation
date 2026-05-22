from langchain_core.tools import tool


@tool
def recommend_interim_care(
    diagnostic_summary: str,
    answers_summary: str,
    red_flags: bool = False,
) -> str:
    """Propose une recommandation intermédiaire prudente (repos, hydratation, surveillance)."""
    base = [
        "Repos relatif et hydratation régulière.",
        "Surveillance des symptômes (température, essoufflement, douleur).",
        "Consultation médicale rapide en cas d'aggravation.",
    ]
    if red_flags:
        base.insert(
            0,
            "Signes d'alerte identifiés : consulter un professionnel de santé sans délai.",
        )
    summary_hint = (diagnostic_summary or answers_summary or "")[:200].lower()
    if any(k in summary_hint for k in ("fièvre", "fievre", "essoufflement", "douleur thoracique")):
        base.append("En cas de fièvre persistante ou de gêne respiratoire, ne pas attendre.")
    return " | ".join(base)
