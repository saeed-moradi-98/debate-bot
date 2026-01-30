# models/database.py
from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import config
import json

Base = declarative_base()

class DebateSession(Base):
    __tablename__ = 'debate_sessions'
    
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    topic = Column(String, nullable=False)
    user_stance = Column(Text)
    bot_stance = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    turn_count = Column(Integer, default=0)
    max_escalation_level = Column(Integer, default=0)
    
class DebateTurn(Base):
    __tablename__ = 'debate_turns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    turn_number = Column(Integer, nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class SentimentRecord(Base):
    __tablename__ = 'sentiment_records'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    turn_number = Column(Integer, nullable=False)
    polarity = Column(Float)
    subjectivity = Column(Float)
    emotions = Column(JSON)  # Store as JSON
    arousal = Column(Float)
    valence = Column(Float)
    toxicity = Column(Float)
    predicted_discomfort = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self, database_url: str = None):
        self.engine = create_engine(database_url or config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_session(self, session_id: str, topic: str, user_stance: str, bot_stance: str, user_id: str = None):
        """Create a new debate session"""
        db = self.SessionLocal()
        try:
            session = DebateSession(
                id=session_id,
                user_id=user_id,
                topic=topic,
                user_stance=user_stance,
                bot_stance=bot_stance
            )
            db.add(session)
            db.commit()
        finally:
            db.close()
    
    def add_turn(self, session_id: str, turn_number: int, role: str, content: str):
        """Record a conversation turn"""
        db = self.SessionLocal()
        try:
            turn = DebateTurn(
                session_id=session_id,
                turn_number=turn_number,
                role=role,
                content=content
            )
            db.add(turn)
            db.commit()
        finally:
            db.close()
    
    def add_sentiment(self, session_id: str, turn_number: int, sentiment_data: dict):
        """Store sentiment analysis results"""
        db = self.SessionLocal()
        try:
            record = SentimentRecord(
                session_id=session_id,
                turn_number=turn_number,
                **sentiment_data
            )
            db.add(record)
            db.commit()
        finally:
            db.close()
    
    def update_session(self, session_id: str, **kwargs):
        """Update session metadata"""
        db = self.SessionLocal()
        try:
            session = db.query(DebateSession).filter_by(id=session_id).first()
            for key, value in kwargs.items():
                setattr(session, key, value)
            db.commit()
        finally:
            db.close()
    
    def get_session_analytics(self, session_id: str) -> dict:
        """Retrieve all analytics for a session"""
        db = self.SessionLocal()
        try:
            session = db.query(DebateSession).filter_by(id=session_id).first()
            turns = db.query(DebateTurn).filter_by(session_id=session_id).all()
            sentiments = db.query(SentimentRecord).filter_by(session_id=session_id).all()
            
            return {
                "session": session,
                "turns": turns,
                "sentiments": sentiments
            }
        finally:
            db.close()