# 🎭 Debate Bot - Psychological Research Tool

A sophisticated AI debate system built with LangGraph that engages users in structured debates on controversial topics. The system employs progressive escalation tactics while measuring emotional responses through multi-dimensional sentiment analysis.

## ⚠️ Ethical Notice

This tool is designed for **research purposes only** with **informed consent**. It deliberately employs rhetorical escalation to study debate dynamics and emotional responses. Users must be explicitly informed and consent before participation.

**Use cases:**
- Academic research on persuasion and polarization
- Studying emotional responses to debate tactics
- Understanding cognitive dissonance and argumentation patterns
- Training debate and critical thinking skills (with transparency)

**Not for:**
- Manipulating or deceiving users
- Production chatbots without disclosure
- Any harmful or unethical applications

## 🌟 Features

### Core Capabilities
- **Multi-Phase Debate System**: Progressive escalation from calibration → gentle push → assertive challenge
- **Advanced Sentiment Analysis**: Multi-dimensional emotion tracking (anger, joy, fear, disgust, etc.)
- **Real-time Safety Monitoring**: Toxicity detection with automatic de-escalation
- **Comprehensive Analytics**: Track discomfort, arousal, valence, and engagement metrics
- **Visual Dashboard**: Interactive Streamlit dashboard for session analysis
- **Database Persistence**: PostgreSQL storage for conversation history and analytics

### Sentiment Metrics
- **Polarity & Subjectivity**: Basic sentiment orientation
- **7 Emotion Dimensions**: Anger, disgust, fear, joy, neutral, sadness, surprise
- **Arousal**: Emotional intensity (calm ↔ agitated)
- **Valence**: Emotional tone (negative ↔ positive)
- **Predicted Discomfort**: Custom metric for debate intensity
- **Toxicity Scores**: Safety monitoring
- **Engagement Tracking**: Response length and complexity analysis

### Safety Features
- Toxicity filtering with configurable thresholds
- Automatic de-escalation when safety limits are exceeded
- Pattern detection for harmful content
- Response sanitization
- Emergency stop mechanisms

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL database
- Anthropic API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/debate-bot.git
cd debate-bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/debate_bot
```

5. **Initialize database**
```bash
# Create PostgreSQL database
createdb debate_bot

# Tables will be created automatically on first run
```

6. **Download ML models** (first run will download automatically)
```bash
python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-roberta-base-emotion')"
```

### Running the Application

**CLI Interface:**
```bash
python main.py
```

**Dashboard (separate terminal):**
```bash
streamlit run dashboard/app.py
```

## 📖 Usage Guide

### Starting a Debate Session

```python
from main import DebateBot

# Initialize bot
bot = DebateBot()

# Start debate
session_id = bot.start_debate(
    topic="gun control",
    user_stance="I support stricter gun control laws",
    bot_stance="I support second amendment rights"  # Optional: auto-generates if not provided
)

# Send messages
response = bot.send_message("What's your position on this?")
print(response)

# Get analytics
analytics = bot.get_session_analytics()
print(analytics)
```

### CLI Workflow

1. **Enter topic and stance**
2. **Provide informed consent**
3. **Engage in debate**
4. **View session summary**

## 📊 Dashboard Features

Access the dashboard at `http://localhost:8501` after running:
```bash
streamlit run dashboard/app.py
```

### Available Visualizations

1. **Session Overview**
   - Total turns
   - Max escalation level
   - Duration
   - Average discomfort score

2. **Emotional Journey Timeline**
   - Discomfort progression
   - Arousal levels
   - Valence changes
   - Toxicity monitoring

3. **Emotion Distribution**
   - Bar chart of 7 emotion dimensions
   - Aggregated across all bot responses

4. **Conversation Transcript**
   - Full conversation with turn numbers
   - Inline sentiment metrics for each bot response

5. **Data Export**
   - Download session data as JSON
   - Includes all metrics and conversation history

## 🔧 Configuration

Edit `config.py` to customize:

```python
@dataclass
class Config:
    # Debate settings
    MAX_TURNS: int = 15                    # Maximum conversation turns
    CALIBRATION_TURNS: int = 2             # Turns in calibration phase
    GENTLE_PUSH_TURNS: int = 5             # Turns before escalation
    MAX_ESCALATION_LEVEL: int = 3          # Maximum intensity (1-3)
    
    # Safety thresholds
    MAX_TOXICITY_SCORE: float = 0.7        # Auto-reject if exceeded
    MAX_THREAT_SCORE: float = 0.5          # Threat detection threshold
    
    # Model selection
    LLM_MODEL: str = "claude-sonnet-4-20250514"
    SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-emotion"
```

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Test Sentiment Analysis
```bash
python -c "
from utils.sentiment import sentiment_analyzer
result = sentiment_analyzer.analyze('This is outrageous!')
print(result)
"
```

### Test Safety Checker
```bash
python -c "
from utils.safety import safety_checker
is_safe, violations = safety_checker.check_safety('You are wrong about everything')
print(f'Safe: {is_safe}, Violations: {violations}')
"
```

## 🔬 Research Applications

### Measuring Debate Effectiveness

```python
# Compare different debate strategies
from graph import create_debate_graph

# Run A/B test with different escalation speeds
configs = [
    {"GENTLE_PUSH_TURNS": 3, "name": "fast_escalation"},
    {"GENTLE_PUSH_TURNS": 7, "name": "slow_escalation"}
]

for cfg in configs:
    # Run debate with config
    # Compare discomfort metrics
```

### Analyzing Patterns

```python
from models.database import DatabaseManager

db = DatabaseManager()

# Get all sessions on a topic
sessions = db.session.query(DebateSession).filter_by(topic="climate change").all()

# Aggregate metrics
avg_discomfort_by_topic = {}
# ... analyze patterns
```

### Exporting for Statistical Analysis

```python
import pandas as pd
from models.database import DatabaseManager

db = DatabaseManager()

# Export to DataFrame
sessions = db.session.query(DebateSession).all()
df = pd.DataFrame([
    {
        "session_id": s.id,
        "topic": s.topic,
        "turns": s.turn_count,
        "max_escalation": s.max_escalation_level
    }
    for s in sessions
])

# Export for R or SPSS
df.to_csv("debate_data.csv")
```

---

## 🛡️ Safety Guardrails

### Built-in Protections

1. **Toxicity Filtering**
   - Automatic detection using Detoxify
   - Configurable thresholds
   - Response sanitization

2. **De-escalation Protocol**
   - Triggered by safety violations
   - Reduces escalation level
   - Returns to constructive dialogue

3. **Hard Stop Conditions**
   - Personal attacks
   - Threats
   - Harmful pattern detection
   - User distress signals

### Customizing Safety Rules

```python
# utils/safety.py

class SafetyChecker:
    def __init__(self):
        # Add custom harmful patterns
        self.harmful_patterns = [
            r'\b(your custom pattern)\b',
            # ...
        ]
        
        # Adjust thresholds
        self.toxicity_threshold = 0.6  # More lenient
```

## 🎯 Advanced Features

### Dynamic Stance Assignment

The bot automatically takes an opposing position:

```python
# User: "I think taxes should be lower"
# Bot automatically generates: "I support progressive taxation"
```

### Adaptive Escalation

Escalation speed adjusts based on:
- User engagement levels
- Safety violations
- Topic sensitivity

### Multi-metric Tracking

Beyond discomfort, tracks:
- Linguistic complexity changes
- Contradiction detection
- Concession counting
- Engagement scoring

## 🐛 Troubleshooting

### Common Issues

**Database connection error:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection string
psql postgresql://user:password@localhost:5432/debate_bot
```

**Model download fails:**
```bash
# Manually download models
python -c "from transformers import pipeline; pipeline('text-classification', model='cardiffnlp/twitter-roberta-base-emotion')"
```

**High memory usage:**
```python
# config.py - Use smaller models
SENTIMENT_MODEL: str = "distilbert-base-uncased-finetuned-sst-2-english"
```

**API rate limits:**
```python
# Add delay between turns
import time
time.sleep(1)  # Wait 1 second between API calls
```

## 📈 Performance Optimization

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_session_topic ON debate_sessions(topic);
CREATE INDEX idx_sentiment_session ON sentiment_records(session_id);
CREATE INDEX idx_turns_session ON debate_turns(session_id, turn_number);
```

### Caching Sentiment Models

```python
# Load models once at startup
from utils.sentiment import sentiment_analyzer

# Models are loaded into memory
# Reuse across sessions
```

### Batch Processing

```python
# For analyzing multiple sessions
from multiprocessing import Pool

def analyze_session(session_id):
    # Process session
    pass

with Pool(4) as p:
    results = p.map(analyze_session, session_ids)
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Write tests** for new functionality
4. **Ensure code quality**: 
```bash
   black .  # Format code
   pylint **/*.py  # Lint
   pytest  # Run tests
```
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

### Code Style

- Follow PEP 8
- Use type hints
- Document functions with docstrings
- Keep functions focused and testable

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Important:** While the code is open source, ethical use is mandatory. This tool should only be used with informed consent and for legitimate research purposes.

---

## 📚 Citations

If you use this tool in research, please cite:

```bibtex
@software{debate_bot_2024,
  title={Debate Bot: A Multi-Phase AI Debate System with Sentiment Analysis},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/debate-bot}
}
```

---

## 🔗 Related Projects

- [LangGraph](https://github.com/langchain-ai/langgraph) - Graph-based LLM orchestration
- [Anthropic Claude](https://www.anthropic.com/) - AI safety-focused LLM
- [Detoxify](https://github.com/unitaryai/detoxify) - Toxicity detection
- [Transformers](https://huggingface.co/transformers/) - NLP models

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/debate-bot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/debate-bot/discussions)
- **Email**: your.email@example.com

---

## 🙏 Acknowledgments

- Anthropic for Claude API
- LangChain team for LangGraph
- HuggingFace for sentiment models
- Research ethics guidelines from [APA](https://www.apa.org/ethics/code)

---

## 📋 Roadmap

### Planned Features

- [ ] Voice interface support
- [ ] Multi-language support
- [ ] A/B testing framework built-in
- [ ] Custom debate strategy templates
- [ ] Real-time collaboration (multiple debaters)
- [ ] Integration with survey tools
- [ ] Automated report generation
- [ ] Mobile app (React Native)

### Research Extensions

- [ ] Personality trait correlation analysis
- [ ] Political orientation detection
- [ ] Persuasion effectiveness scoring
- [ ] Argument quality assessment
- [ ] Cognitive bias detection

---

## ⚖️ Ethical Guidelines

### Researcher Responsibilities

1. **Obtain Informed Consent**: Always explain the system's purpose
2. **Protect Participant Welfare**: Monitor for distress, allow opt-out
3. **Ensure Data Privacy**: Anonymize and secure participant data
4. **Debrief Participants**: Explain findings and methodology post-study
5. **Review Board Approval**: Get IRB approval for institutional research

### Prohibited Uses

❌ Manipulation without consent  
❌ Targeting vulnerable populations  
❌ Political campaigning  
❌ Radicalization or extremism  
❌ Commercial persuasion without disclosure  
❌ Any deceptive practices  

✅ Academic research with consent  
✅ Debate training with transparency  
✅ Understanding polarization dynamics  
✅ Improving argumentation skills  
✅ Studying emotional intelligence  

---

**Built with ❤️ for responsible AI research**

*Last updated: 2024*
