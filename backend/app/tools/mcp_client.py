"""Client léger pour appeler l'outil MCP lookup_clinical_guideline."""

from __future__ import annotations

import json
from pathlib import Path

MCP_DATA_DIR = Path(__file__).resolve().parents[3] / "mcp_server" / "data"


def lookup_clinical_guideline(symptom_category: str) -> dict:
    """
    Équivalent local de l'outil MCP : charge les fiches depuis mcp_server/data.
    En production, remplacer par un client MCP stdio/HTTP.
    """
    path = MCP_DATA_DIR / "guidelines.json"
    if not path.exists():
        return {"category": symptom_category, "guidance": [], "source": "local_fallback"}
    data = json.loads(path.read_text(encoding="utf-8"))
    key = symptom_category.lower().strip()
    entry = data.get(key) or data.get("default", {})
    return {
        "category": symptom_category,
        "guidance": entry.get("guidance", []),
        "red_flags": entry.get("red_flags", []),
        "source": "mcp_server/data/guidelines.json",
    }


def enrich_summary_with_mcp(patient_case: str, answers: list[str]) -> dict:
    """Détecte une catégorie simple et enrichit via MCP."""
    text = f"{patient_case} {' '.join(answers)}".lower()
    if any(w in text for w in ("toux", "respir", "gorge", "nez")):
        category = "respiratory"
    elif any(w in text for w in ("douleur thoracique", "palpitation", "syncope")):
        category = "cardiac"
    else:
        category = "general"
    return lookup_clinical_guideline(category)
