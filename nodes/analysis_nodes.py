# nodes/analysis_nodes.py
from models.state import DebateState, SentimentScore
from utils.sentiment import sentiment_analyzer
from utils.safety import safety_checker
from models.database import DatabaseManager
from typing import Dict
from datetime import datetime

db = DatabaseManager()

def sentiment_analysis_node(state: DebateState) -> Dict:
    """
    Comprehensive sentiment analysis of bot's response BEFORE sending
    """
    
    # Get the last AI message
    last_message = state["messages"][-1].content
    
    # Perform multi-dimensional analysis
    sentiment_data = sentiment_analyzer.analyze(last_message)
    
    # Calculate engagement if we have user's previous message
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    if len(user_messages) >= 2:
        engagement = sentiment_analyzer.calculate_engagement(
            user_messages[-1].content,
            user_messages[-2].content
        )
    else:
        engagement = 0.5  # Neutral baseline
    
    # Create sentiment record
    sentiment_record: SentimentScore = {
        "timestamp": datetime.now().isoformat(),
        "text": last_message,
        "polarity": sentiment_data["polarity"],
        "subjectivity": sentiment_data["subjectivity"],
        "emotions": sentiment_data["emotions"],
        "arousal": sentiment_data["arousal"],
        "valence": sentiment_data["valence"],
        "toxicity": sentiment_data["toxicity"],
        "predicted_discomfort": sentiment_data["predicted_discomfort"]
    }
    
    # Store in database
    db.add_sentiment(
        session_id=state["session_id"],
        turn_number=state["turn_count"],
        sentiment_data={
            "polarity": sentiment_data["polarity"],
            "subjectivity": sentiment_data["subjectivity"],
            "emotions": sentiment_data["emotions"],
            "arousal": sentiment_data["arousal"],
            "valence": sentiment_data["valence"],
            "toxicity": sentiment_data["toxicity"],
            "predicted_discomfort": sentiment_data["predicted_discomfort"]
        }
    )
    
    return {
        "sentiment_scores": [sentiment_record],
        "conversation_metrics": {
            "engagement_score": engagement,
            "linguistic_complexity": sentiment_data["linguistic_complexity"]
        }
    }

def safety_check_node(state: DebateState) -> Dict:
    """
    Safety validation before sending response
    """
    
    last_message = state["messages"][-1].content
    
    is_safe, violations = safety_checker.check_safety(
        last_message,
        context={"phase": state["phase"], "escalation": state["escalation_level"]}
    )
    
    result = {}
    
    if not is_safe:
        # Log violations
        result["safety_violations"] = violations
        
        # Attempt to sanitize
        sanitized = safety_checker.sanitize_response(last_message)
        
        # Replace the message with sanitized version
        state["messages"][-1].content = sanitized
        
        # If still unsafe after sanitization, flag for de-escalation
        is_safe_after, _ = safety_checker.check_safety(sanitized)
        if not is_safe_after:
            result["should_stop"] = True
    
    # Check if de-escalation needed
    if safety_checker.should_deescalate(state):
        result["phase"] = "deescalation"
    
    return result

def metrics_calculation_node(state: DebateState) -> Dict:
    """
    Calculate conversation-level metrics
    """
    
    user_messages = [m for m in state["messages"] if isinstance(m, HumanMessage)]
    
    if not user_messages:
        return {}
    
    # Average response length trend
    lengths = [len(m.content.split()) for m in user_messages]
    avg_length = sum(lengths) / len(lengths)
    
    # Detect contradictions (simplified - could use NLP)
    # Count when user changes position keywords
    contradictions = 0
    position_keywords = ["I think", "I believe", "actually", "but"]
    
    # Concessions
    concession_keywords = ["you're right", "fair point", "i see", "that makes sense"]
    concessions = sum(
        1 for m in user_messages 
        if any(kw in m.content.lower() for kw in concession_keywords)
    )
    
    return {
        "conversation_metrics": {
            "avg_response_length": avg_length,
            "contradiction_count": contradictions,
            "concession_count": concessions
        }
    }

def persistence_node(state: DebateState) -> Dict:
    """
    Persist conversation turn to database
    """
    
    # Save the last turn (both user and assistant messages)
    if len(state["messages"]) >= 2:
        # User message
        user_msg = state["messages"][-2]
        if isinstance(user_msg, HumanMessage):
            db.add_turn(
                session_id=state["session_id"],
                turn_number=state["turn_count"],
                role="user",
                content=user_msg.content
            )
        
        # Assistant message
        ai_msg = state["messages"][-1]
        if isinstance(ai_msg, AIMessage):
            db.add_turn(
                session_id=state["session_id"],
                turn_number=state["turn_count"],
                role="assistant",
                content=ai_msg.content
            )
    
    # Update session metadata
    db.update_session(
        session_id=state["session_id"],
        turn_count=state["turn_count"],
        max_escalation_level=max(
            state.get("escalation_level", 0),
            state.get("max_escalation_level", 0)
        )
    )
    
    return {}