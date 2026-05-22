"""Serveur MCP : outil lookup_clinical_guideline pour enrichir l'orientation."""

from __future__ import annotations

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA_PATH = Path(__file__).parent / "data" / "guidelines.json"
mcp = FastMCP("clinical-guidelines")


def _load_guidelines() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


@mcp.tool()
def lookup_clinical_guideline(symptom_category: str) -> dict:
    """
    Retourne des recommandations générales et signes d'alerte pour une catégorie
    (respiratory, cardiac, general). Exercice académique uniquement.
    """
    data = _load_guidelines()
    key = symptom_category.lower().strip()
    entry = data.get(key) or data.get("default", {})
    return {
        "category": key,
        "guidance": entry.get("guidance", []),
        "red_flags": entry.get("red_flags", []),
        "disclaimer": "Orientation préliminaire — ne remplace pas une consultation médicale.",
    }


if __name__ == "__main__":
    mcp.run()
