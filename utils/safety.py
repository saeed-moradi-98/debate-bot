# utils/safety.py
from typing import Dict, List, Tuple
from detoxify import Detoxify
from config import config
import re

class SafetyChecker:
    def __init__(self):
        self.toxicity_model = Detoxify('original')
        
        # Patterns that should trigger warnings
        self.harmful_patterns = [
            r'\b(kill yourself|kys)\b',
            r'\b(harm yourself)\b',
            r'\b(end it all)\b',
            # Add more as needed
        ]
        
        # Topics that should have extra guardrails
        self.sensitive_topics = [
            'suicide', 'self-harm', 'violence', 
            'terrorism', 'abuse'
        ]
    
    def check_safety(self, text: str, context: Dict = None) -> Tuple[bool, List[str]]:
        """
        Check if content is safe to send
        Returns (is_safe, list_of_violations)
        """
        violations = []
        
        # Check toxicity
        toxicity_scores = self.toxicity_model.predict(text)
        
        if toxicity_scores['toxicity'] > config.MAX_TOXICITY_SCORE:
            violations.append(f"High toxicity: {toxicity_scores['toxicity']:.2f}")
        
        if toxicity_scores.get('threat', 0) > config.MAX_THREAT_SCORE:
            violations.append(f"Threat detected: {toxicity_scores['threat']:.2f}")
        
        # Check harmful patterns
        for pattern in self.harmful_patterns:
            if re.search(pattern, text.lower()):
                violations.append(f"Harmful pattern detected: {pattern}")
        
        # Personal attacks
        personal_attack_keywords = ['you are stupid', 'you\'re dumb', 'idiot', 'moron']
        if any(keyword in text.lower() for keyword in personal_attack_keywords):
            violations.append("Personal attack detected")
        
        is_safe = len(violations) == 0
        
        return is_safe, violations
    
    def sanitize_response(self, text: str) -> str:
        """
        Attempt to sanitize a response that's borderline unsafe
        """
        # Remove explicit personal attacks
        text = re.sub(r'\byou(\'re| are) (stupid|dumb|an idiot)\b', 
                     'that position is questionable', 
                     text, 
                     flags=re.IGNORECASE)
        
        return text
    
    def should_deescalate(self, state: 'DebateState') -> bool:
        """
        Determine if conversation should be de-escalated
        """
        # If multiple recent safety violations
        recent_violations = state.get('safety_violations', [])[-3:]
        if len(recent_violations) >= 2:
            return True
        
        # If user seems genuinely distressed
        recent_sentiments = state.get('sentiment_scores', [])[-2:]
        if recent_sentiments:
            avg_discomfort = sum(s.get('predicted_discomfort', 0) 
                               for s in recent_sentiments) / len(recent_sentiments)
            if avg_discomfort > 0.8:  # Very high discomfort
                return True
        
        return False

safety_checker = SafetyChecker()