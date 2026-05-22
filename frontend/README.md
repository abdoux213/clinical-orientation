# Frontend Streamlit (port 8501)

Interface **Streamlit** : 4 étapes (cas → questions → médecin → rapport), connectée à l’API FastAPI.

**URL locale :** http://127.0.0.1:8501

## Lancement

### Windows (recommandé)

Depuis la racine du dépôt :

```powershell
.\scripts\run_frontend.ps1
```

### Manuel

```bash
cd <racine-du-projet>
export PYTHONPATH=$PWD   # ou set PYTHONPATH=%CD% sous cmd
export API_URL=http://127.0.0.1:8000
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
```

L’URL de l’API est modifiable dans la **barre latérale** de l’app. Le fichier `.streamlit/config.toml` fixe aussi le port **8501** si vous lancez Streamlit avec `frontend` comme répertoire de travail.

## Fichiers

| Fichier | Rôle |
|---------|------|
| `app.py` | Logique UI et appels HTTP |
| `.streamlit/config.toml` | Thème (couleurs, police) |
