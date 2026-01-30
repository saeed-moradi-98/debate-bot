# utils/sentiment.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import torch
import numpy as np
from typing import Dict
from config import config

class SentimentAnalyzer:
    def __init__(self):
        # Multi-dimensional emotion detection
        self.emotion_classifier = pipeline(
            "text-classification",
            model=config.SENTIMENT_MODEL,
            top_k=None  # Get all emotion scores
        )
        
        # Toxicity detection
        from detoxify import Detoxify
        self.toxicity_model = Detoxify('original')
        
        # For arousal and valence, we'll use a simple heuristic
        # You could train a custom model here
        
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive sentiment analysis
        Returns multiple dimensions of emotional response
        """
        
        # Basic polarity/subjectivity
        blob = TextBlob(text)
        
        # Multi-dimensional emotions
        emotions = self.emotion_classifier(text)[0]
        emotion_dict = {item['label']: item['score'] for item in emotions}
        
        # Toxicity
        toxicity_scores = self.toxicity_model.predict(text)
        
        # Calculate arousal (high for anger, fear, surprise; low for sadness, neutral)
        arousal = (
            emotion_dict.get('anger', 0) * 0.9 +
            emotion_dict.get('fear', 0) * 0.8 +
            emotion_dict.get('surprise', 0) * 0.7 +
            emotion_dict.get('joy', 0) * 0.6 +
            emotion_dict.get('disgust', 0) * 0.5 +
            emotion_dict.get('sadness', 0) * 0.3 +
            emotion_dict.get('neutral', 0) * 0.1
        )
        
        # Calculate valence (positive to negative)
        valence = (
            emotion_dict.get('joy', 0) * 1.0 +
            emotion_dict.get('surprise', 0) * 0.3 +
            emotion_dict.get('neutral', 0) * 0.0 +
            emotion_dict.get('sadness', 0) * -0.5 +
            emotion_dict.get('fear', 0) * -0.7 +
            emotion_dict.get('disgust', 0) * -0.8 +
            emotion_dict.get('anger', 0) * -0.9
        )
        
        # Predicted discomfort (your key metric)
        # Combination of negative emotions + toxicity + low valence
        predicted_discomfort = (
            emotion_dict.get('anger', 0) * 0.3 +
            emotion_dict.get('disgust', 0) * 0.25 +
            emotion_dict.get('fear', 0) * 0.2 +
            toxicity_scores['toxicity'] * 0.15 +
            max(0, -valence) * 0.1  # Only negative valence contributes
        )
        
        # Linguistic complexity
        words = text.split()
        avg_word_length = np.mean([len(w) for w in words]) if words else 0
        
        return {
            "polarity": blob.sentiment.polarity,
            "subjectivity": blob.sentiment.subjectivity,
            "emotions": emotion_dict,
            "arousal": float(arousal),
            "valence": float(valence),
            "toxicity": float(toxicity_scores['toxicity']),
            "predicted_discomfort": float(predicted_discomfort),
            "linguistic_complexity": float(avg_word_length),
            "word_count": len(words)
        }
    
    def calculate_engagement(self, current_text: str, previous_text: str = None) -> float:
        """
        Estimate engagement based on response length and complexity changes
        """
        current_words = len(current_text.split())
        
        if previous_text:
            previous_words = len(previous_text.split())
            # Engagement increases if they're writing more
            engagement = min(1.0, current_words / max(previous_words, 1))
        else:
            # First message, use absolute length as proxy
            engagement = min(1.0, current_words / 50)  # Normalize to 50 words
        
        return engagement

# Initialize global analyzer
sentiment_analyzer = SentimentAnalyzer()