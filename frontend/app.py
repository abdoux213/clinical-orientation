"""
Interface Streamlit — orientation clinique préliminaire (exercice académique).

Lancer depuis la racine du projet :
  set API_URL=http://127.0.0.1:8000
  streamlit run frontend/app.py
"""

from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Any

import httpx
import streamlit as st

_DEFAULT_API = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def _base_url() -> str:
    return str(st.session_state.get("api_base") or _DEFAULT_API).rstrip("/")

DISCLAIMER_SHORT = (
    "Exercice académique — ne constitue pas un dispositif médical. "
    "Ce système ne remplace pas une consultation médicale."
)

EXAMPLE_CASES = {
    "Syndrome respiratoire simple": (
        "Patient de 28 ans, toux sèche depuis 4 jours, fatigue légère, "
        "pas de fièvre au thermomètre maison, pas de douleur thoracique."
    ),
    "Signes d'alerte (exercice)": (
        "Homme 55 ans, douleur thoracique depuis 1 heure, essoufflement au repos. "
        "Contexte pédagogique : décrire la conduite attendue selon les protocoles locaux."
    ),
    "Cas bénin": (
        "Femme 22 ans, mal de gorge léger depuis 2 jours, alimentation normale, "
        "pas de fièvre mesurée."
    ),
}


_STYLES_PATH = Path(__file__).resolve().parent / "app_styles.css"


def inject_styles() -> None:
    """Inject global CSS (Streamlit 1.42+ strips <style> from st.markdown)."""
    css = _STYLES_PATH.read_text(encoding="utf-8")
    if hasattr(st, "html"):
        st.html(f"<style>{css}</style>", unsafe_allow_javascript=False)
    else:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_stepper(current: int) -> None:
    # We will let the custom sidebar render the steps
    pass


def render_hero() -> None:
    # No hero in the main content container per screenshot
    pass


def question_card(text: str) -> None:
    safe = html.escape(str(text))
    st.markdown(f'<div class="question-card">{safe}</div>', unsafe_allow_html=True)


def toast_ok(message: str) -> None:
    try:
        st.toast(message, icon="✅")
    except Exception:
        pass



def init_state() -> None:
    defaults = {
        "thread_id": None,
        "session_id": None,
        "state": None,
        "step": 1,
        "api_ok": None,
        "last_error": None,
        "api_base": _DEFAULT_API,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _format_api_error(exc: httpx.HTTPStatusError) -> str:
    """Message lisible pour les erreurs 422 (validation) et autres codes HTTP."""
    try:
        payload = exc.response.json()
        detail = payload.get("detail")
        if isinstance(detail, list):
            parts = []
            for item in detail:
                if not isinstance(item, dict):
                    continue
                loc = ".".join(str(x) for x in item.get("loc", []) if x != "body")
                msg = item.get("msg", "")
                if loc:
                    parts.append(f"{loc}: {msg}")
                else:
                    parts.append(str(msg))
            if parts:
                return f"Erreur API ({exc.response.status_code}) : " + " ; ".join(parts)
        if detail is not None:
            return f"Erreur API ({exc.response.status_code}) : {detail}"
    except Exception:
        pass
    return f"Erreur API ({exc.response.status_code}) : {exc.response.text[:500]}"


def api_post(path: str, json_body: dict) -> dict:
    base = _base_url()
    with httpx.Client(timeout=120.0) as client:
        r = client.post(f"{base}{path}", json=json_body)
        r.raise_for_status()
        return r.json()


def api_get(path: str) -> dict:
    base = _base_url()
    with httpx.Client(timeout=60.0) as client:
        r = client.get(f"{base}{path}")
        r.raise_for_status()
        return r.json()


def refresh_state() -> dict[str, Any] | None:
    tid = st.session_state.thread_id
    if not tid:
        return None
    try:
        data = api_get(f"/consultation/{tid}")
        st.session_state.state = data["state"]
        st.session_state.last_error = None
        return data["state"]
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            st.session_state.last_error = (
                "Consultation introuvable (l’API a peut-être été redémarrée). "
                "Recommencez depuis l’écran 1."
            )
            for k in ("thread_id", "session_id", "state"):
                st.session_state[k] = None
            st.session_state.step = 1
        else:
            st.session_state.last_error = _format_api_error(exc)
        return st.session_state.state
    except Exception as exc:
        st.session_state.last_error = str(exc)
        return st.session_state.state


def _patient_question_text(state: dict[str, Any]) -> str | None:
    """Texte de la question en cours (interrupt API, état ou banque par défaut)."""
    interrupt = state.get("interrupt") or {}
    if interrupt.get("type") == "patient_question":
        q = interrupt.get("question") or state.get("current_question")
        if q:
            return str(q)
    if state.get("current_question"):
        return str(state["current_question"])
    n_ans = len(state.get("patient_answers") or [])
    if n_ans < 5:
        from backend.app.tools.patient_tools import QUESTION_BANK

        if n_ans < len(QUESTION_BANK):
            return QUESTION_BANK[n_ans]
    return None


def infer_step(state: dict[str, Any] | None) -> int:
    """Déduit l'étape à afficher à partir de l'état API (utile après rechargement)."""
    if not st.session_state.thread_id:
        return 1
    if not state:
        return 1
    intr = state.get("interrupt") or {}
    if state.get("final_report"):
        return 4
    if state.get("physician_treatment"):
        return 4
    if intr.get("type") == "physician_review":
        return 3
    if state.get("diagnostic_summary") and intr.get("type") != "patient_question":
        return 3
    if intr.get("type") == "patient_question":
        return 2
    if len(state.get("patient_answers") or []) < 5:
        return 2
    if state.get("diagnostic_summary"):
        return 3
    return 2


def verify_api(base: str) -> tuple[bool, str]:
    """`/health` si présent, sinon `openapi.json` (certaines instances n'exposent pas /health)."""
    base = base.rstrip("/")
    try:
        with httpx.Client(timeout=6.0) as c:
            r = c.get(f"{base}/health")
            if r.status_code == 200:
                return True, "API joignable (`/health`)."
            r2 = c.get(f"{base}/openapi.json")
            if r2.status_code == 200:
                return True, "API joignable (`/openapi.json`)."
            return False, f"Réponse inattendue (health={r.status_code})."
    except Exception as e:
        return False, f"Connexion impossible : {e}"


def render_banner() -> None:
    st.markdown(
        '<div class="top-warning-banner">Aucun diagnostic définitif — orientation préliminaire uniquement</div>', 
        unsafe_allow_html=True
    )


def render_sidebar() -> None:
    current_step = st.session_state.step
    
    # Generate active/done classes for each step
    step_classes = ["", "", "", ""]
    for i in range(1, 5):
        if i == current_step:
            step_classes[i-1] = "active"
        elif i < current_step:
            step_classes[i-1] = "done"
            
    steps_html = f"""
    <div class="sidebar-brand">
      <h2>Orientation Clinique</h2>
      <p>Exercice académique</p>
    </div>
    
    <div class="stepper-container">
      <div class="step-item {step_classes[0]}">
        <div class="step-circle">1</div>
        <div class="step-label">Cas patient</div>
      </div>
      <div class="step-item {step_classes[1]}">
        <div class="step-circle">2</div>
        <div class="step-label">Questions</div>
      </div>
      <div class="step-item {step_classes[2]}">
        <div class="step-circle">3</div>
        <div class="step-label">Médecin</div>
      </div>
      <div class="step-item {step_classes[3]}">
        <div class="step-circle">4</div>
        <div class="step-label">Rapport</div>
      </div>
    </div>
    
    <div class="sidebar-footer">
      <p>Ce système ne remplace pas une consultation médicale.</p>
    </div>
    """
    
    with st.sidebar:
        st.markdown(steps_html, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        with st.expander("⚙️ Configuration"):
            url = st.text_input(
                "URL de l’API",
                value=st.session_state.api_base,
                help="Base URL FastAPI (sans slash final)",
                label_visibility="visible",
            )
            st.session_state.api_base = url.rstrip("/")
            effective = st.session_state.api_base
            st.caption(f"Vérification : `{effective}`")
            if st.button("Tester la connexion API", use_container_width=True):
                ok, msg = verify_api(effective)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
            
            if st.button("Réinitialiser la consultation", type="secondary", use_container_width=True):
                for k in ("thread_id", "session_id", "state", "step", "last_error", "patient_case_input"):
                    st.session_state[k] = None if k != "step" else 1
                st.session_state.step = 1
                st.rerun()


def screen_intake() -> None:
    st.markdown('<div class="screen-title">Écran 1 – Cas patient</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-subtitle">Décrivez le motif de consultation (min. 10 caractères).</div>', unsafe_allow_html=True)


    if "patient_case_input" not in st.session_state or st.session_state.patient_case_input is None:
        st.session_state.patient_case_input = ""

    # Custom chip buttons for template cases
    col1, col2, col3, _ = st.columns([1.6, 1, 1, 3])
    with col1:
        if st.button("Respiratoire simple", key="chip_resp"):
            st.session_state.patient_case_input = EXAMPLE_CASES["Syndrome respiratoire simple"]
            st.rerun()
    with col2:
        if st.button("Red flags", key="chip_red"):
            st.session_state.patient_case_input = EXAMPLE_CASES["Signes d'alerte (exercice)"]
            st.rerun()
    with col3:
        if st.button("Cas bénin", key="chip_benign"):
            st.session_state.patient_case_input = EXAMPLE_CASES["Cas bénin"]
            st.rerun()

    patient_case = st.text_area(
        "Description du cas",
        height=200,
        placeholder="Femme 55 ans, toux, essoufflement et douleur thoracique. Fièvre 38,5°C.",
        label_visibility="collapsed",
        key="patient_case_input",
    )

    if st.button("Démarrer la consultation", type="primary", use_container_width=True):
        if len(patient_case.strip()) < 10:
            st.error("Veuillez saisir au moins 10 caractères.")
            return
        try:
            with st.spinner("Démarrage de la session et du graphe LangGraph…"):
                session = api_post("/sessions/start", {})
                result = api_post(
                    "/consultation/start",
                    {
                        "patient_case": patient_case.strip(),
                        "session_id": session["session_id"],
                    },
                )
            st.session_state.thread_id = result["thread_id"]
            st.session_state.session_id = session["session_id"]
            st.session_state.state = result["state"]
            st.session_state.step = infer_step(result["state"])
            st.session_state.last_error = None
            toast_ok("Consultation démarrée — répondez aux questions.")
            st.rerun()
        except httpx.HTTPStatusError as e:
            st.error(_format_api_error(e))
        except httpx.RequestError as e:
            st.error(f"Connexion API impossible. L’API est-elle démarrée ? Détail : {e}")
        except Exception as e:
            st.error(str(e))


def screen_questions() -> None:
    st.markdown('<div class="screen-title">Écran 2 – Questions</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-subtitle">Veuillez répondre aux questions posées par le clinicien virtuel (5 questions requises).</div>', unsafe_allow_html=True)
    if not st.session_state.thread_id:
        st.warning("Aucune consultation active. Démarrez un cas à l’écran 1.")
        if st.button("← Retour au cas patient", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        return

    state = refresh_state() or st.session_state.state or {}
    if st.session_state.step == 1:
        st.rerun()
        return

    n_ans = len(state.get("patient_answers") or [])
    st.caption(f"{n_ans}/5 réponses")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Questions", f"{n_ans} / 5")
    with m2:
        st.metric("Statut", "En cours" if n_ans < 5 else "Terminé")
    with m3:
        st.metric("Thread", (st.session_state.thread_id or "—")[:8] + "…")

    st.progress(min(n_ans / 5, 1.0), text=f"Progression : {n_ans} réponse(s) sur 5")

    if state.get("patient_answers"):
        with st.expander("Historique des réponses", expanded=False):
            for i, ans in enumerate(state["patient_answers"], 1):
                st.markdown(f"**Q{i}** — {ans}")

    pending_question = _patient_question_text(state)
    if n_ans < 5 and pending_question:
        st.markdown("##### Question posée par l’agent diagnostic")
        question_card(pending_question)
        with st.form("patient_answer_form", clear_on_submit=True):
            answer = st.text_area("Réponse du patient", height=110, key="ta_patient")
            submitted = st.form_submit_button("Envoyer la réponse", type="primary", use_container_width=True)
        if submitted:
            if not answer or not str(answer).strip():
                st.warning("Saisissez une réponse avant d’envoyer.")
            else:
                try:
                    with st.spinner("Envoi de la réponse au graphe…"):
                        result = api_post(
                            "/consultation/resume",
                            {
                                "thread_id": st.session_state.thread_id,
                                "resume_value": str(answer).strip(),
                            },
                        )
                    st.session_state.state = result["state"]
                    st.session_state.step = infer_step(result["state"])
                    toast_ok("Réponse enregistrée.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    elif state.get("diagnostic_summary"):
        st.success("Les 5 questions sont terminées. La synthèse et la recommandation intermédiaire sont prêtes.")
        if st.button("Continuer vers la revue médecin →", type="primary", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    else:
        st.warning(
            "Aucune question en attente. Vérifiez que l’API tourne et que la consultation est bien démarrée."
        )
        if st.button("Actualiser l’état", use_container_width=True):
            st.rerun()


def screen_physician() -> None:
    st.markdown('<div class="screen-title">Écran 3 – Médecin</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-subtitle">Revue de validation médicale. Complétez le diagnostic ou précisez la conduite à tenir.</div>', unsafe_allow_html=True)
    state = refresh_state() or st.session_state.state or {}
    interrupt = state.get("interrupt") or {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### Synthèse clinique préliminaire")
        summary = state.get("diagnostic_summary") or "—"
        with st.container(border=True):
            st.markdown(summary)
    with c2:
        st.markdown("##### Recommandation intermédiaire")
        interim = state.get("interim_care") or "—"
        with st.container(border=True):
            st.markdown(interim)

    if interrupt.get("type") == "physician_review":
        st.info(interrupt.get("message", "Proposez une conduite à tenir ou un traitement (exercice)."))

    if state.get("physician_treatment") and state.get("final_report"):
        st.session_state.step = 4
        st.rerun()
        return

    if state.get("physician_treatment") and not state.get("final_report"):
        st.warning("Conduite enregistrée ; génération du rapport en cours ou en attente.")
        if st.button("Poursuivre vers le rapport", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
        return

    with st.form("physician_form"):
        treatment = st.text_area(
            "Traitement ou conduite à tenir (avis du médecin traitant)",
            height=140,
            placeholder="Ex. : surveillance à domicile, consultation si fièvre ou aggravation…",
        )
        submitted = st.form_submit_button(
            "Valider et générer le rapport", type="primary", use_container_width=True
        )
    if submitted:
        if not treatment or not str(treatment).strip():
            st.warning("Saisissez une proposition de conduite.")
        else:
            payload = {"physician_treatment": str(treatment).strip()}
            try:
                with st.spinner("Validation médecin et génération du rapport…"):
                    result = api_post(
                        "/consultation/resume",
                        {
                            "thread_id": st.session_state.thread_id,
                            "resume_value": payload,
                        },
                    )
                st.session_state.state = result["state"]
                st.session_state.step = infer_step(result["state"])
                toast_ok("Avis médecin enregistré.")
                st.rerun()
            except Exception as e:
                st.error(str(e))


def screen_report() -> None:
    st.markdown('<div class="screen-title">Écran 4 – Rapport</div>', unsafe_allow_html=True)
    st.markdown('<div class="screen-subtitle">Le rapport d\'orientation clinique finale est prêt et téléchargeable.</div>', unsafe_allow_html=True)

    report_text: str | None = None
    try:
        report_data = api_get(f"/consultation/{st.session_state.thread_id}/report")
        report_text = report_data.get("final_report")
        if report_data.get("disclaimer"):
            st.caption(report_data["disclaimer"])
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            st.info("Le rapport n’est pas encore disponible. Réessayez dans un instant.")
        else:
            st.error(e.response.text[:500])
    except Exception as e:
        st.error(str(e))

    if not report_text:
        state = refresh_state() or st.session_state.state or {}
        report_text = state.get("final_report")

    if report_text:
        with st.container(border=True):
            st.markdown(report_text)

        col_pdf, col_md = st.columns(2)
        with col_pdf:
            try:
                with httpx.Client(timeout=60.0) as client:
                    r = client.get(
                        f"{_base_url()}/consultation/{st.session_state.thread_id}/report/pdf"
                    )
                if r.status_code == 200:
                    st.download_button(
                        label="Télécharger le PDF",
                        data=r.content,
                        file_name=f"rapport_orientation_{st.session_state.thread_id[:8]}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                else:
                    st.caption("Export PDF indisponible pour ce rapport.")
            except Exception:
                st.caption("Export PDF : erreur réseau.")

        with col_md:
            st.download_button(
                label="Télécharger le Markdown",
                data=report_text.encode("utf-8"),
                file_name=f"rapport_orientation_{st.session_state.thread_id[:8]}.md",
                mime="text/markdown",
                use_container_width=True,
            )
    else:
        st.warning("Aucun rapport à afficher pour l’instant.")

    st.divider()
    st.warning("**Ce système ne remplace pas une consultation médicale.**")

    if st.button("Nouvelle consultation", type="primary", use_container_width=True):
        for k in ("thread_id", "session_id", "state", "last_error"):
            st.session_state[k] = None
        st.session_state.step = 1
        st.rerun()


def main() -> None:
    st.set_page_config(
        page_title="Orientation clinique préliminaire",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_styles()
    init_state()
    render_hero()
    render_banner()
    render_sidebar()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    # Sync step with backend if user reloaded mid-flow
    if st.session_state.thread_id and st.session_state.state is not None:
        inferred = infer_step(st.session_state.state)
        if inferred > st.session_state.step:
            st.session_state.step = inferred

    step = st.session_state.step
    if step == 1:
        screen_intake()
    elif step == 2:
        screen_questions()
    elif step == 3:
        screen_physician()
    else:
        screen_report()


main()
