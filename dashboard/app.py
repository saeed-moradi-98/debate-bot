# dashboard/app.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from models.database import DatabaseManager
from datetime import datetime

st.set_page_config(page_title="Debate Analytics Dashboard", layout="wide")

db = DatabaseManager()

st.title("🎭 Debate Bot Analytics Dashboard")

# Session selector
session_id = st.text_input("Enter Session ID to analyze:")

if session_id:
    analytics = db.get_session_analytics(session_id)
    
    if analytics["session"]:
        session = analytics["session"]
        sentiments = analytics["sentiments"]
        turns = analytics["turns"]
        
        # Session Overview
        st.header("Session Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Turns", session.turn_count)
        with col2:
            st.metric("Max Escalation", f"{session.max_escalation_level}/3")
        with col3:
            duration = (session.ended_at - session.started_at).seconds if session.ended_at else 0
            st.metric("Duration (min)", f"{duration // 60}")
        with col4:
            avg_discomfort = sum(s.predicted_discomfort for s in sentiments) / len(sentiments) if sentiments else 0
            st.metric("Avg Discomfort", f"{avg_discomfort:.2f}")
        
        st.markdown(f"**Topic:** {session.topic}")
        st.markdown(f"**User Stance:** {session.user_stance}")
        st.markdown(f"**Bot Stance:** {session.bot_stance}")
        
        # Sentiment Timeline
        st.header("Emotional Journey")
        
        if sentiments:
            df_sentiment = pd.DataFrame([
                {
                    "turn": s.turn_number,
                    "discomfort": s.predicted_discomfort,
                    "arousal": s.arousal,
                    "valence": s.valence,
                    "toxicity": s.toxicity
                }
                for s in sentiments
            ])
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_sentiment["turn"],
                y=df_sentiment["discomfort"],
                mode='lines+markers',
                name='Predicted Discomfort',
                line=dict(color='red', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_sentiment["turn"],
                y=df_sentiment["arousal"],
                mode='lines+markers',
                name='Arousal',
                line=dict(color='orange', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=df_sentiment["turn"],
                y=df_sentiment["valence"],
                mode='lines+markers',
                name='Valence',
                line=dict(color='blue', width=2)
            ))
            
            fig.update_layout(
                title="Emotional Metrics Over Time",
                xaxis_title="Turn Number",
                yaxis_title="Score",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Emotion Breakdown
            st.header("Emotion Distribution")
            
            # Aggregate emotions across all turns
            all_emotions = {}
            for s in sentiments:
                for emotion, score in s.emotions.items():
                    all_emotions[emotion] = all_emotions.get(emotion, 0) + score
            
            # Normalize
            total = sum(all_emotions.values())
            all_emotions = {k: v/total for k, v in all_emotions.items()}
            
            fig_emotions = px.bar(
                x=list(all_emotions.keys()),
                y=list(all_emotions.values()),
                labels={'x': 'Emotion', 'y': 'Average Score'},
                title='Average Emotion Distribution in Bot Responses'
            )
            
            st.plotly_chart(fig_emotions, use_container_width=True)
        
        # Conversation Transcript
        st.header("Conversation Transcript")
        
        for turn in turns:
            if turn.role == "user":
                st.markdown(f"**👤 User (Turn {turn.turn_number}):**")
                st.info(turn.content)
            else:
                st.markdown(f"**🤖 Bot (Turn {turn.turn_number}):**")
                
                # Find corresponding sentiment
                sent = next((s for s in sentiments if s.turn_number == turn.turn_number), None)
                
                if sent:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.warning(turn.content)
                    with col2:
                        st.metric("Discomfort", f"{sent.predicted_discomfort:.2f}")
                        st.metric("Toxicity", f"{sent.toxicity:.2f}")
                else:
                    st.warning(turn.content)
        
        # Export Data
        st.header("Export Data")
        
        if st.button("Download Session Data as JSON"):
            import json
            
            export_data = {
                "session": {
                    "id": session.id,
                    "topic": session.topic,
                    "user_stance": session.user_stance,
                    "bot_stance": session.bot_stance,
                    "turn_count": session.turn_count,
                    "started_at": session.started_at.isoformat(),
                    "ended_at": session.ended_at.isoformat() if session.ended_at else None
                },
                "turns": [
                    {
                        "turn_number": t.turn_number,
                        "role": t.role,
                        "content": t.content,
                        "timestamp": t.timestamp.isoformat()
                    }
                    for t in turns
                ],
                "sentiments": [
                    {
                        "turn_number": s.turn_number,
                        "predicted_discomfort": s.predicted_discomfort,
                        "arousal": s.arousal,
                        "valence": s.valence,
                        "toxicity": s.toxicity,
                        "emotions": s.emotions
                    }
                    for s in sentiments
                ]
            }
            
            st.download_button(
                "Download",
                data=json.dumps(export_data, indent=2),
                file_name=f"debate_{session_id}.json",
                mime="application/json"
            )
    
    else:
        st.error("Session not found")

# Aggregate Analytics
st.header("Aggregate Analytics (All Sessions)")

if st.button("Load All Sessions Summary"):
    # This would query all sessions - implement based on your needs
    st.info("Coming soon: Cross-session analytics")