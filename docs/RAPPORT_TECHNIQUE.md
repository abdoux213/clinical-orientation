# Rapport technique — orientation clinique préliminaire

## 1. Objectif

Application multi-agents **LangGraph** simulant un workflow d'**orientation clinique préliminaire** (exercice académique, sans diagnostic définitif).

## 2. Architecture

```
Frontend (Streamlit) → FastAPI → Graphe LangGraph
                              ↘ Tools locaux + données MCP (guidelines.json)
MCP Server (stdio) — lookup_clinical_guideline
```

| Composant | Rôle |
|-----------|------|
| **Supervisor** | Route vers diagnostic, médecin, rapport ou fin |
| **Diagnostic Agent** | 5× `ask_patient` + synthèse + `recommend_interim_care` |
| **Physician Review** | Human-in-the-loop (`interrupt`) |
| **Report Agent** | Rapport structuré + disclaimer obligatoire |

## 3. État partagé (`MedicalState`)

Champs principaux : `patient_case`, `patient_answers`, `question_count`, `diagnostic_summary`, `interim_care`, `physician_treatment`, `final_report`, `next`, `messages`.

## 4. Human-in-the-loop

- **Patient** : `interrupt()` dans `diagnostic_agent` à chaque question (boucle 5).
- **Médecin** : `interrupt()` dans `physician_review` avec synthèse + recommandation intermédiaire.

Reprise via `Command(resume=...)` exposée par `POST /consultation/resume`.

## 5. MCP

Serveur `mcp_server/server.py` expose `lookup_clinical_guideline`. Le backend charge les mêmes données via `mcp_client.py` (équivalent local ; branchable en client MCP stdio en production).

## 6. API FastAPI

Endpoints conformes au cahier des charges : sessions, start/resume consultation, état et rapport.

## 7. Choix techniques

- **LLM** : OpenAI optionnel (`OPENAI_API_KEY`) ; mode démo déterministe sans clé.
- **Frontend** : Streamlit pour enchaîner les 4 écrans rapidement.
- **Persistance** : `MemorySaver` (threads par `thread_id`) — extensible vers Postgres.

## 8. Éthique

Libellés : orientation clinique préliminaire, synthèse clinique, recommandation intermédiaire. Mention systématique : *« Ce système ne remplace pas une consultation médicale. »*

## 9. Pistes bonus

JSON Pydantic pour le rapport, Postgres, export PDF, Docker, tests pytest sur les nœuds et l'API.
