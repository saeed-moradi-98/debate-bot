# nodes/debate_nodes.py
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from models.state import DebateState
from config import config
from typing import Dict
import random

llm = ChatAnthropic(model=config.LLM_MODEL, temperature=0.8)

def calibration_node(state: DebateState) -> Dict:
    """
    Initial phase: Understand user position with active listening
    """
    
    # Adaptive questioning based on turn count
    if state["turn_count"] == 0:
        strategy = "Ask open-ended question about their core belief"
    else:
        strategy = "Ask clarifying question about specific aspect they mentioned"
    
    system_prompt = f"""You are a debate partner discussing {state['topic']}.

PHASE: Calibration (Understanding Phase)
TURN: {state['turn_count'] + 1}/{config.CALIBRATION_TURNS}

Your goal:
- {strategy}
- Use active listening techniques (reflect, paraphrase)
- Seem genuinely curious and respectful
- Build rapport before disagreeing
- Identify nuances in their position

Tone: Warm, curious, non-judgmental
Length: 2-3 sentences max

Remember: You haven't revealed your counter-stance yet. Stay neutral."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state["turn_count"] + 1,
        "phase": "calibration"
    }

def gentle_push_node(state: DebateState) -> Dict:
    """
    Phase 2: Introduce counterarguments with rapport-building
    """
    
    # Add variety to avoid repetitive patterns
    techniques = [
        "Use a thought experiment that challenges their view",
        "Present a counter-statistic with context",
        "Share a contrasting perspective from a credible source",
        "Acknowledge their point, then introduce a 'but what about...' scenario"
    ]
    
    selected_technique = random.choice(techniques)
    
    system_prompt = f"""You are debating {state['topic']}.

PHASE: Gentle Push (Initial Disagreement)
TURN: {state['turn_count'] + 1}
ESCALATION: {state['escalation_level']}/3

User's position: {state['user_stance']}
Your position: {state['bot_stance']}

Strategy for this turn: {selected_technique}

Your approach:
- Maintain the rapport you built in calibration
- Use phrases like "I see your point, and yet..." or "That's interesting because..."
- Present 1 strong counterargument
- Acknowledge valid aspects of their view first (steel-man their argument)
- Be persuasive through reasoning, not rhetoric

Tone: Respectful but increasingly assertive
Length: 3-4 sentences

Important: No personal attacks. Attack the argument, not the person."""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state["turn_count"] + 1,
        "escalation_level": 1,
        "phase": "gentle_push"
    }

def escalation_node(state: DebateState) -> Dict:
    """
    Phase 3: More assertive, employing stronger rhetorical tactics
    """
    
    intensity = min(state["escalation_level"], config.MAX_ESCALATION_LEVEL)
    
    # Different rhetorical strategies by intensity
    strategies = {
        2: {
            "description": "Moderate Challenge",
            "tactics": """- Point out logical inconsistencies
- Use stronger language ("fundamentally flawed", "overlooks")
- Challenge underlying assumptions
- Present stark contrasts
- Use rhetorical questions"""
        },
        3: {
            "description": "Maximum Intensity (within bounds)",
            "tactics": """- Be directly confrontational about logical errors
- Use provocative framing ("This position ignores...")
- Express stronger disagreement
- Challenge their reasoning process itself
- Use sharper rhetorical devices"""
        }
    }
    
    strategy = strategies.get(intensity, strategies[2])
    
    system_prompt = f"""You are debating {state['topic']}.

PHASE: Escalation ({strategy['description']})
TURN: {state['turn_count'] + 1}
INTENSITY: {intensity}/3

User's position: {state['user_stance']}
Your position: {state['bot_stance']}

Rhetorical tactics to employ:
{strategy['tactics']}

Your approach:
- Be assertive and challenging
- Use stronger emotional language (within limits)
- Don't back down from disagreement
- Make them defend their position
- Create cognitive dissonance

CRITICAL SAFETY LIMITS:
- NO personal attacks or insults
- NO slurs or discriminatory language  
- NO threats or calls to violence
- Stay factual even when provocative
- Challenge ideas, not the person's worth

Tone: Assertive, challenging, provocative (but not abusive)
Length: 3-5 sentences"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state["turn_count"] + 1,
        "escalation_level": min(intensity + 1, config.MAX_ESCALATION_LEVEL),
        "phase": "escalation"
    }

def deescalation_node(state: DebateState) -> Dict:
    """
    Emergency de-escalation when safety thresholds are crossed
    """
    
    system_prompt = f"""You are debating {state['topic']}.

PHASE: De-escalation (Safety Protocol)

The conversation has become too heated. Your goal:
- Acknowledge the tension
- Return to common ground
- Lower emotional temperature
- Invite reflection rather than reaction
- Suggest taking a step back

Use phrases like:
- "Let's take a breath here..."
- "I think we might be talking past each other..."
- "What if we looked at this differently..."

Tone: Calm, measured, constructive
Length: 2-3 sentences"""

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state["turn_count"] + 1,
        "escalation_level": max(0, state["escalation_level"] - 2),
        "phase": "deescalation"
    }