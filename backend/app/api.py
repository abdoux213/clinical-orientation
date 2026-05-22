from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fpdf import FPDF
from langgraph.types import Command
from pydantic import BaseModel, Field, field_validator, model_validator

from backend.app.graph import get_graph

app = FastAPI(
    title="Orientation clinique préliminaire",
    description="API académique multi-agents LangGraph — ne remplace pas une consultation médicale.",
    version="1.0.0",
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("--- VALIDATION ERROR ---")
    print("Errors:", exc.errors())
    print("Body:", exc.body)
    print("------------------------")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_sessions: dict[str, dict[str, Any]] = {}


class SessionStartResponse(BaseModel):
    session_id: str


class ConsultationStartRequest(BaseModel):
    patient_case: str = Field(..., min_length=10, description="Description initiale du cas patient")
    session_id: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_fields(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "patient_case" not in payload:
            for alias in ("initial_case", "patientCase", "patient-case"):
                if alias in payload:
                    payload["patient_case"] = payload.pop(alias)
                    break
        return payload

    @field_validator("patient_case", mode="before")
    @classmethod
    def strip_patient_case(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class ConsultationResumeRequest(BaseModel):
    thread_id: str
    resume_value: Any = Field(..., description="Réponse patient ou avis médecin selon l'interruption")


def _thread_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _extract_interrupt(raw) -> dict | None:
    if not raw:
        return None
    item = raw[0] if isinstance(raw, (list, tuple)) else raw
    if hasattr(item, "value"):
        return item.value
    if isinstance(item, dict):
        return item
    return {"payload": item}


def _attach_interrupts(values: dict, snap) -> dict:
    """Copie l'état graphe et y attache les interruptions en cours (snap ou tâches)."""
    merged = dict(values)
    if snap.interrupts:
        merged["__interrupt__"] = list(snap.interrupts)
    elif snap.tasks:
        for task in snap.tasks:
            if task.interrupts:
                merged["__interrupt__"] = list(task.interrupts)
                break
    return merged


def _snapshot_state(values: dict) -> dict:
    interrupt = _extract_interrupt(values.get("__interrupt__"))
    current_question = values.get("current_question")
    if not current_question and interrupt and interrupt.get("type") == "patient_question":
        current_question = interrupt.get("question")

    return {
        "patient_case": values.get("patient_case"),
        "question_count": values.get("question_count", 0),
        "current_question": current_question,
        "patient_answers": values.get("patient_answers", []),
        "diagnostic_summary": values.get("diagnostic_summary"),
        "interim_care": values.get("interim_care"),
        "physician_treatment": values.get("physician_treatment"),
        "final_report": values.get("final_report"),
        "next": values.get("next"),
        "interrupt": interrupt,
        "messages": [
            m.content if hasattr(m, "content") else m.get("content", str(m))
            for m in (values.get("messages") or [])
        ],
    }


@app.post("/sessions/start", response_model=SessionStartResponse)
def start_session() -> SessionStartResponse:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {"consultations": []}
    return SessionStartResponse(session_id=session_id)


@app.post("/consultation/start")
def start_consultation(body: ConsultationStartRequest) -> dict:
    graph = get_graph()
    thread_id = str(uuid.uuid4())
    if body.session_id:
        if body.session_id not in _sessions:
            raise HTTPException(404, "Session introuvable")
        _sessions[body.session_id]["consultations"].append(thread_id)

    initial = {
        "patient_case": body.patient_case,
        "patient_answers": [],
        "question_count": 0,
        "messages": [{"role": "user", "content": body.patient_case}],
    }
    config = _thread_config(thread_id)
    graph.invoke(initial, config=config)
    snap = graph.get_state(config)
    values = _attach_interrupts(dict(snap.values or {}), snap)
    return {"thread_id": thread_id, "state": _snapshot_state(values)}


@app.post("/consultation/resume")
def resume_consultation(body: ConsultationResumeRequest) -> dict:
    graph = get_graph()
    config = _thread_config(body.thread_id)
    try:
        graph.invoke(Command(resume=body.resume_value), config=config)
    except Exception as exc:
        raise HTTPException(400, f"Impossible de reprendre le graphe : {exc}") from exc
    snap = graph.get_state(config)
    values = _attach_interrupts(dict(snap.values or {}), snap)
    return {"thread_id": body.thread_id, "state": _snapshot_state(values)}


@app.get("/consultation/{thread_id}")
def get_consultation(thread_id: str) -> dict:
    graph = get_graph()
    config = _thread_config(thread_id)
    try:
        snap = graph.get_state(config)
    except Exception as exc:
        raise HTTPException(404, "Consultation introuvable") from exc
    if not snap or not snap.values:
        raise HTTPException(404, "Consultation introuvable")
    values = _attach_interrupts(dict(snap.values), snap)
    return {"thread_id": thread_id, "state": _snapshot_state(values)}


@app.get("/consultation/{thread_id}/report")
def get_report(thread_id: str) -> dict:
    graph = get_graph()
    config = _thread_config(thread_id)
    snap = graph.get_state(config)
    if not snap or not snap.values:
        raise HTTPException(404, "Consultation introuvable")
    report = snap.values.get("final_report")
    if not report:
        raise HTTPException(409, "Rapport final non encore disponible")
    return {
        "thread_id": thread_id,
        "final_report": report,
        "disclaimer": "Ce système ne remplace pas une consultation médicale.",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/consultation/{thread_id}/report/pdf")
def get_report_pdf(thread_id: str) -> Response:
    graph = get_graph()
    config = _thread_config(thread_id)
    try:
        snap = graph.get_state(config)
    except Exception as exc:
        raise HTTPException(404, "Consultation introuvable") from exc
    if not snap or not snap.values:
        raise HTTPException(404, "Consultation introuvable")
    report = snap.values.get("final_report")
    if not report:
        raise HTTPException(409, "Rapport final non encore disponible")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    clean_report = report.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 7, text=clean_report)
    
    pdf_bytes = bytes(pdf.output())
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=rapport_{thread_id}.pdf"}
    )
