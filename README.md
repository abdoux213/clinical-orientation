# Orientation clinique préliminaire — Multi-agents LangGraph

**Exercice académique** — ce système n'est pas un dispositif médical et **ne remplace pas une consultation médicale**.

Workflow : collecte patient (5 questions) → synthèse clinique préliminaire → recommandation intermédiaire → revue médecin (human-in-the-loop) → rapport final.

## Structure

```
clinical-orientation/
├── backend/          # LangGraph + FastAPI
├── mcp_server/       # Outil MCP guidelines
├── frontend/         # Streamlit (4 écrans)
├── docs/             # Rapport technique + scénarios de test
└── README.md
```

## Prérequis

- Python 3.11+
- (Optionnel) Clé `OPENAI_API_KEY` pour enrichir synthèse et rapport

## Installation

```bash
cd clinical-orientation
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r backend/requirements.txt
copy .env.example .env          # puis renseigner OPENAI_API_KEY si besoin
```

## Lancer l'API

Depuis la racine du projet :

```bash
set PYTHONPATH=%CD%             # Windows cmd
# export PYTHONPATH=$(pwd)      # bash
uvicorn backend.app.api:app --reload --host 127.0.0.1 --port 8000
```

## Lancer le frontend

### Option A — Streamlit (port **8501**)

Depuis la racine du dépôt (API sur le port 8000) :

```powershell
set PYTHONPATH=%CD%
set API_URL=http://127.0.0.1:8000
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
```

Ou sous **PowerShell** :

```powershell
.\scripts\run_frontend.ps1
```

**URL de l’interface :** [http://127.0.0.1:8501](http://127.0.0.1:8501)

### Option B — React (Vite) **recommandé**

```powershell
.\scripts\run_frontend_react.ps1
```

Ou :

```bash
cd frontend-react
npm install
npm run dev
```

**URL :** http://127.0.0.1:5173 — voir [frontend-react/README.md](frontend-react/README.md).

L’interface Streamlit (8501) et React partagent la même API. React mémorise l’URL API dans `localStorage` ou via `VITE_API_URL`.

## Serveur MCP

```bash
python mcp_server/server.py
```

Outil exposé : `lookup_clinical_guideline(symptom_category)`.

## LangGraph Studio

```bash
set PYTHONPATH=<racine-du-projet>
cd backend
langgraph dev
```

Ouvrir l'UI indiquée par la CLI, graphe `clinical_orientation`. Tester les **interrupts** patient et médecin.

Fichier : `backend/langgraph.json`.

## API

| Méthode | Route | Description |
|---------|-------|-------------|
| POST | `/sessions/start` | Nouvelle session |
| POST | `/consultation/start` | Démarre une consultation (`patient_case`) |
| POST | `/consultation/resume` | Reprend après interrupt (`resume_value`) |
| GET | `/consultation/{thread_id}` | État courant |
| GET | `/consultation/{thread_id}/report` | Rapport final |

Documentation interactive : http://127.0.0.1:8000/docs

## Scénarios de test

Voir [docs/SCENARIOS_TEST.md](docs/SCENARIOS_TEST.md) (respiratoire simple, red flags, cas bénin).

## Rapport technique

Voir [docs/RAPPORT_TECHNIQUE.md](docs/RAPPORT_TECHNIQUE.md).

## Agents et tools

- **Supervisor** — routage
- **Diagnostic Agent** — `ask_patient`, `recommend_interim_care`, enrichissement MCP
- **Physician Review** — interrupt médecin
- **Report Agent** — rapport + disclaimer

## Licence / usage

Usage pédagogique uniquement.
