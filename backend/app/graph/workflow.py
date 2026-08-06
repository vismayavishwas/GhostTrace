from langgraph.graph import StateGraph, END
from app.graph.state import GhostTraceStateDict


def create_placeholder_graph():
    """
    Creates an empty placeholder LangGraph StateGraph instance.
    Real agent nodes will be attached in future intelligence phases.
    """
    workflow = StateGraph(GhostTraceStateDict)
    
    # Placeholder pass-through node for initial compilation check
    def idle_node(state: GhostTraceStateDict) -> GhostTraceStateDict:
        return {"current_state": "IDLE"}
    
    workflow.add_node("idle", idle_node)
    workflow.set_entry_point("idle")
    workflow.add_edge("idle", END)
    
    return workflow.compile()



# Compiled placeholder graph export
graph_app = create_placeholder_graph()
