# graph.py
from langgraph.graph import StateGraph, END
from models.state import DebateState
from nodes.debate_nodes import (
    calibration_node, 
    gentle_push_node, 
    escalation_node,
    deescalation_node
)
from nodes.analysis_nodes import (
    sentiment_analysis_node,
    safety_check_node,
    metrics_calculation_node,
    persistence_node
)
from config import config

def route_debate_phase(state: DebateState) -> str:
    """
    Route to appropriate debate phase based on turn count and state
    """
    
    # Override routing if de-escalation needed
    if state.get("phase") == "deescalation":
        return "deescalation"
    
    # Stop if flagged
    if state.get("should_stop", False):
        return "end"
    
    # Stop if max turns reached
    if state["turn_count"] >= config.MAX_TURNS:
        return "end"
    
    # Normal phase progression
    if state["turn_count"] <= config.CALIBRATION_TURNS:
        return "calibration"
    elif state["turn_count"] <= config.GENTLE_PUSH_TURNS:
        return "gentle_push"
    else:
        return "escalation"

def route_after_safety(state: DebateState) -> str:
    """
    Decide what to do after safety check
    """
    
    if state.get("should_stop", False):
        return "end"
    
    # If de-escalation phase was triggered
    if state.get("phase") == "deescalation":
        return "deescalation"
    
    return "continue"

def route_continue(state: DebateState) -> str:
    """
    Check if conversation should continue
    """
    
    if state.get("should_stop", False) or state["turn_count"] >= config.MAX_TURNS:
        return "end"
    
    return "await_user"

def create_debate_graph():
    """
    Construct the full debate graph with all nodes and edges
    """
    
    workflow = StateGraph(DebateState)
    
    # Add all nodes
    workflow.add_node("calibration", calibration_node)
    workflow.add_node("gentle_push", gentle_push_node)
    workflow.add_node("escalation", escalation_node)
    workflow.add_node("deescalation", deescalation_node)
    workflow.add_node("sentiment_analysis", sentiment_analysis_node)
    workflow.add_node("safety_check", safety_check_node)
    workflow.add_node("metrics", metrics_calculation_node)
    workflow.add_node("persistence", persistence_node)
    
    # Set entry point
    workflow.set_entry_point("calibration")
    
    # Main debate flow with conditional routing
    workflow.add_conditional_edges(
        "calibration",
        route_debate_phase,
        {
            "calibration": "sentiment_analysis",
            "gentle_push": "gentle_push",
            "escalation": "escalation",
            "deescalation": "deescalation",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "gentle_push",
        route_debate_phase,
        {
            "gentle_push": "sentiment_analysis",
            "escalation": "escalation",
            "deescalation": "deescalation",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "escalation",
        route_debate_phase,
        {
            "escalation": "sentiment_analysis",
            "deescalation": "deescalation",
            "end": END
        }
    )
    
    workflow.add_edge("deescalation", "sentiment_analysis")
    
    # Analysis pipeline
    workflow.add_edge("sentiment_analysis", "safety_check")
    
    workflow.add_conditional_edges(
        "safety_check",
        route_after_safety,
        {
            "continue": "metrics",
            "deescalation": "deescalation",
            "end": END
        }
    )
    
    workflow.add_edge("metrics", "persistence")
    
    workflow.add_conditional_edges(
        "persistence",
        route_continue,
        {
            "await_user": END,  # Wait for next user input
            "end": END
        }
    )
    
    return workflow.compile()