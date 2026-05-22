# Frontend React (Vite + TypeScript)

Interface web pour le projet **orientation clinique préliminaire** — 4 étapes connectées à l’API FastAPI.

| Étape | Écran |
|-------|--------|
| 1 | Cas patient initial |
| 2 | 5 questions / réponses (interrupt LangGraph) |
| 3 | Revue médecin (human-in-the-loop) |
| 4 | Rapport final (.md + PDF) |

## Prérequis

- Node.js 18+
- API backend : `http://127.0.0.1:8000` (ou `VITE_API_URL`)

## Lancement

```powershell
# Depuis la racine du projet
.\scripts\run_frontend_react.ps1
```

Ou manuellement :

```bash
cd frontend-react
npm install
npm run dev
```

**URL :** http://127.0.0.1:5173

## Build production

```bash
npm run build
npm run preview
```

Variable au build : `VITE_API_URL=https://votre-api.example.com`

## Structure

```
src/
  App.tsx              # Orchestration
  api.ts               # Client HTTP
  components/
    Sidebar.tsx
    Stepper.tsx
    steps/             # Intake, Questions, Physician, Report
```

L’URL API est mémorisée dans `localStorage` (modifiable dans la sidebar).
