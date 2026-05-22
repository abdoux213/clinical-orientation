from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from backend.app.nodes.diagnostic_agent import diagnostic_agent_node
from backend.app.nodes.physician_review import physician_review_node
from backend.app.nodes.report_agent import report_agent_node
from backend.app.nodes.supervisor import supervisor_node
from backend.app.state import MedicalState

_checkpointer = MemorySaver()
_compiled_graph = None


def _route_from_supervisor(state: MedicalState) -> str:
    nxt = state.get("next") or "diagnostic_agent"
    if nxt == "FINISH":
        return "FINISH"
    return nxt


def build_graph():
    workflow = StateGraph(MedicalState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diagnostic_agent", diagnostic_agent_node)
    workflow.add_node("physician_review", physician_review_node)
    workflow.add_node("report_agent", report_agent_node)

    workflow.add_edge(START, "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        _route_from_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        },
    )
    workflow.add_edge("diagnostic_agent", "supervisor")
    workflow.add_edge("physician_review", "supervisor")
    workflow.add_edge("report_agent", "supervisor")

    return workflow.compile(checkpointer=_checkpointer)


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


# Export LangGraph Studio
clinical_orientation = get_graph
