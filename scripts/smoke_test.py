"""Test d'intégration minimal (sans serveur HTTP)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langgraph.types import Command

from backend.app.graph import get_graph


def run_case(patient_case: str, answers: list[str], physician: str) -> dict:
    graph = get_graph()
    thread_id = "test-thread"
    config = {"configurable": {"thread_id": thread_id}}

    graph.invoke(
        {
            "patient_case": patient_case,
            "patient_answers": [],
            "messages": [{"role": "user", "content": patient_case}],
        },
        config=config,
    )

    for ans in answers:
        snap = graph.get_state(config)
        if not snap.interrupts:
            break
        graph.invoke(Command(resume=ans), config=config)

    snap = graph.get_state(config)
    if snap.interrupts:
        graph.invoke(Command(resume={"physician_treatment": physician}), config=config)

    final = graph.get_state(config)
    values = dict(final.values or {})
    assert len(values.get("patient_answers", [])) == 5, "5 réponses attendues"
    assert values.get("diagnostic_summary"), "synthèse manquante"
    assert values.get("interim_care"), "recommandation intermédiaire manquante"
    assert values.get("physician_treatment"), "avis médecin manquant"
    assert values.get("final_report"), "rapport final manquant"
    assert "ne remplace pas" in values["final_report"].lower()
    return values


if __name__ == "__main__":
    v = run_case(
        "Toux sèche depuis 4 jours, fatigue légère.",
        ["4 jours", "Non", "Stable", "Aucun", "Non"],
        "Surveillance à domicile, consultation si fièvre.",
    )
    print("OK — rapport généré,", len(v["final_report"]), "caractères")
