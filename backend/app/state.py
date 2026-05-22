from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    patient_case: str
    question_count: int
    current_question: str
    patient_answers: list[str]
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    final_report: str
    pending_interrupt: Literal["patient", "physician", None]
