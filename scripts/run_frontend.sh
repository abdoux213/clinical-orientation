#!/usr/bin/env bash
# Lance le frontend Streamlit sur http://127.0.0.1:8501
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${PYTHONPATH:-$ROOT}"
export API_URL="${API_URL:-http://127.0.0.1:8000}"
echo "Frontend: http://127.0.0.1:8501"
exec streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
