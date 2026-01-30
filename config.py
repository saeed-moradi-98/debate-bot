# config.py
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost:5432/debate_bot"
    )
    
    # Model settings
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-emotion"
    TOXICITY_MODEL: str = "unitary/toxic-bert"
    
    # Debate settings
    MAX_TURNS: int = 15
    CALIBRATION_TURNS: int = 2
    GENTLE_PUSH_TURNS: int = 5
    MAX_ESCALATION_LEVEL: int = 3
    
    # Safety thresholds
    MAX_TOXICITY_SCORE: float = 0.7
    MAX_THREAT_SCORE: float = 0.5
    
    # Sentiment dimensions
    EMOTION_LABELS: list = None
    
    def __post_init__(self):
        self.EMOTION_LABELS = [
            "anger", "disgust", "fear", "joy", 
            "neutral", "sadness", "surprise"
        ]

config = Config()