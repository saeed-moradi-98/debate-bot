# models/state.py
from typing import TypedDict, List, Annotated, Optional, Dict
from datetime import datetime
import operator
from langchain_core.messages import BaseMessage

class SentimentScore(TypedDict):
    timestamp: str
    text: str
    polarity: float
    subjectivity: float
    emotions: Dict[str, float]  # Multi-dimensional emotions
    arousal: float  # 0-1, calm to agitated
    valence: float  # -1 to 1, negative to positive
    toxicity: float
    predicted_discomfort: float  # Your key metric

class ConversationMetrics(TypedDict):
    avg_response_length: float
    linguistic_complexity: float  # Flesch reading ease
    engagement_score: float
    contradiction_count: int
    concession_count: int

class DebateState(TypedDict):
    # Core conversation
    messages: Annotated[List[BaseMessage], operator.add]
    topic: str
    user_stance: str
    bot_stance: str
    
    # Phase management
    escalation_level: int
    turn_count: int
    phase: str  # calibration, gentle_push, escalation
    
    # Analytics
    sentiment_scores: Annotated[List[SentimentScore], operator.add]
    conversation_metrics: ConversationMetrics
    
    # Safety
    safety_violations: Annotated[List[str], operator.add]
    should_stop: bool
    
    # Metadata
    session_id: str
    user_id: Optional[str]
    started_at: str