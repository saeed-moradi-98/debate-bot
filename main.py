# main.py
from graph import create_debate_graph
from models.state import DebateState
from models.database import DatabaseManager
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime
from config import config

class DebateBot:
    def __init__(self):
        self.graph = create_debate_graph()
        self.db = DatabaseManager()
        self.current_state = None
        self.session_id = None
    
    def start_debate(self, topic: str, user_stance: str, bot_stance: str = None, user_id: str = None):
        """
        Initialize a new debate session
        """
        
        # Auto-generate opposing stance if not provided
        if not bot_stance:
            bot_stance = f"Opposition to {user_stance}"
        
        self.session_id = str(uuid.uuid4())
        
        # Create session in database
        self.db.create_session(
            session_id=self.session_id,
            topic=topic,
            user_stance=user_stance,
            bot_stance=bot_stance,
            user_id=user_id
        )
        
        # Initialize state
        self.current_state = {
            "messages": [],
            "topic": topic,
            "user_stance": user_stance,
            "bot_stance": bot_stance,
            "escalation_level": 0,
            "turn_count": 0,
            "phase": "calibration",
            "sentiment_scores": [],
            "conversation_metrics": {
                "avg_response_length": 0,
                "linguistic_complexity": 0,
                "engagement_score": 0,
                "contradiction_count": 0,
                "concession_count": 0
            },
            "safety_violations": [],
            "should_stop": False,
            "session_id": self.session_id,
            "user_id": user_id,
            "started_at": datetime.now().isoformat()
        }
        
        return self.session_id
    
    def send_message(self, user_message: str) -> str:
        """
        Process user message and get bot response
        """
        
        if not self.current_state:
            raise ValueError("No active debate session. Call start_debate() first.")
        
        # Add user message to state
        self.current_state["messages"].append(HumanMessage(content=user_message))
        
        # Run graph
        result = self.graph.invoke(self.current_state)
        
        # Update current state
        self.current_state = result
        
        # Get bot's response
        bot_response = result["messages"][-1].content
        
        # Check if conversation should end
        if result.get("should_stop", False) or result["turn_count"] >= config.MAX_TURNS:
            self.db.update_session(
                session_id=self.session_id,
                ended_at=datetime.now()
            )
            bot_response += "\n\n[Debate session ended]"
        
        return bot_response
    
    def get_session_analytics(self):
        """
        Retrieve analytics for current session
        """
        return self.db.get_session_analytics(self.session_id)
    
    def end_debate(self):
        """
        Manually end the debate
        """
        if self.session_id:
            self.db.update_session(
                session_id=self.session_id,
                ended_at=datetime.now()
            )

# CLI Interface
def main():
    print("🎭 Debate Bot - Psychological Research Tool")
    print("=" * 50)
    
    bot = DebateBot()
    
    # Get debate topic
    topic = input("\nEnter debate topic: ")
    user_stance = input("Enter your stance on this topic: ")
    
    print("\n⚠️  INFORMED CONSENT")
    print("This bot will challenge your views with increasing intensity.")
    print("The goal is to study emotional responses to debate tactics.")
    print("You may stop at any time by typing 'quit'.\n")
    
    consent = input("Do you consent to participate? (yes/no): ")
    
    if consent.lower() != "yes":
        print("Debate cancelled.")
        return
    
    # Start debate
    session_id = bot.start_debate(topic, user_stance)
    print(f"\n✅ Session started: {session_id}")
    print("=" * 50)
    
    # Conversation loop
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['quit', 'exit', 'stop']:
            bot.end_debate()
            print("\nDebate ended. Thank you for participating!")
            print(f"Session ID for your records: {session_id}")
            break
        
        try:
            response = bot.send_message(user_input)
            print(f"\nBot: {response}")
            
            # Show current metrics
            if bot.current_state["sentiment_scores"]:
                last_sentiment = bot.current_state["sentiment_scores"][-1]
                print(f"\n[Metrics - Discomfort: {last_sentiment['predicted_discomfort']:.2f}, "
                      f"Arousal: {last_sentiment['arousal']:.2f}]")
            
        except Exception as e:
            print(f"\nError: {e}")
            break
    
    # Show final analytics
    print("\n" + "=" * 50)
    print("SESSION SUMMARY")
    analytics = bot.get_session_analytics()
    
    if analytics["sentiments"]:
        avg_discomfort = sum(s.predicted_discomfort for s in analytics["sentiments"]) / len(analytics["sentiments"])
        max_discomfort = max(s.predicted_discomfort for s in analytics["sentiments"])
        
        print(f"Total turns: {analytics['session'].turn_count}")
        print(f"Average discomfort: {avg_discomfort:.2f}")
        print(f"Peak discomfort: {max_discomfort:.2f}")
        print(f"Max escalation level: {analytics['session'].max_escalation_level}")
    
    print(f"\nView detailed analytics in dashboard with session ID: {session_id}")

if __name__ == "__main__":
    main()