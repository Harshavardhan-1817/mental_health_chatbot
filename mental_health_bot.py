import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
import random
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import defaultdict
import time

# # Configure Streamlit page
# st.set_page_config(
#     page_title="MindCare Pro - Mental Health Support",
#     page_icon="🧠",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #4CAF50;
    }
    
    .bot-message {
        background-color: #e8f4fd;
        border-left-color: #2196F3;
    }
    
    .therapy-exercise {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .mood-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .journal-entry {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #6c757d;
        margin: 0.5rem 0;
    }
    
    .emergency-notice {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .technique-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

class MoodTracker:
    def __init__(self):
        if 'mood_data' not in st.session_state:
            st.session_state.mood_data = []
    
    def log_mood(self, mood_score, emotion, notes=""):
        """Log a mood entry"""
        entry = {
            'timestamp': datetime.now(),
            'mood_score': mood_score,
            'emotion': emotion,
            'notes': notes
        }
        st.session_state.mood_data.append(entry)
    
    def get_mood_history(self, days=7):
        """Get mood history for the last N days"""
        if not st.session_state.mood_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(st.session_state.mood_data)
        df['date'] = df['timestamp'].dt.date
        cutoff_date = datetime.now().date() - timedelta(days=days)
        return df[df['date'] >= cutoff_date]
    
    def create_mood_chart(self):
        """Create mood visualization"""
        df = self.get_mood_history(14)  # 2 weeks
        if df.empty:
            return None
        
        # Group by date and get average mood
        daily_mood = df.groupby('date')['mood_score'].mean().reset_index()
        
        fig = px.line(daily_mood, x='date', y='mood_score', 
                     title='Mood Trend (Past 2 Weeks)',
                     labels={'mood_score': 'Mood Score (1-10)', 'date': 'Date'},
                     line_shape='spline')
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            height=300
        )
        
        fig.add_hline(y=5, line_dash="dash", line_color="gray", 
                     annotation_text="Neutral")
        
        return fig
    
    def get_mood_insights(self):
        """Generate insights from mood data"""
        df = self.get_mood_history(7)
        if df.empty:
            return "Start logging your mood to see insights!"
        
        avg_mood = df['mood_score'].mean()
        mood_trend = "stable"
        
        if len(df) > 3:
            recent_avg = df.tail(3)['mood_score'].mean()
            older_avg = df.head(3)['mood_score'].mean()
            
            if recent_avg > older_avg + 0.5:
                mood_trend = "improving"
            elif recent_avg < older_avg - 0.5:
                mood_trend = "declining"
        
        common_emotion = df['emotion'].mode().iloc[0] if not df['emotion'].empty else "mixed"
        
        return f"""
        **Weekly Mood Insights:**
        • Average mood: {avg_mood:.1f}/10
        • Trend: {mood_trend}
        • Most common emotion: {common_emotion}
        • Total entries: {len(df)}
        """

class JournalManager:
    def __init__(self):
        if 'journal_entries' not in st.session_state:
            st.session_state.journal_entries = []
    
    def add_entry(self, title, content, mood_score, tags=[]):
        """Add a journal entry"""
        entry = {
            'id': len(st.session_state.journal_entries),
            'timestamp': datetime.now(),
            'title': title,
            'content': content,
            'mood_score': mood_score,
            'tags': tags,
            'word_count': len(content.split())
        }
        st.session_state.journal_entries.append(entry)
        return entry['id']
    
    def get_entries(self, limit=5):
        """Get recent journal entries"""
        entries = sorted(st.session_state.journal_entries, 
                        key=lambda x: x['timestamp'], reverse=True)
        return entries[:limit]
    
    def search_entries(self, query):
        """Search journal entries"""
        results = []
        query_lower = query.lower()
        
        for entry in st.session_state.journal_entries:
            if (query_lower in entry['title'].lower() or 
                query_lower in entry['content'].lower() or 
                any(query_lower in tag.lower() for tag in entry['tags'])):
                results.append(entry)
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_journal_stats(self):
        """Get journaling statistics"""
        if not st.session_state.journal_entries:
            return "No journal entries yet. Start writing to see your stats!"
        
        total_entries = len(st.session_state.journal_entries)
        total_words = sum(entry['word_count'] for entry in st.session_state.journal_entries)
        avg_mood = sum(entry['mood_score'] for entry in st.session_state.journal_entries) / total_entries
        
        # Get date range
        dates = [entry['timestamp'].date() for entry in st.session_state.journal_entries]
        date_range = (max(dates) - min(dates)).days + 1
        
        return f"""
        **Journaling Statistics:**
        • Total entries: {total_entries}
        • Total words written: {total_words:,}
        • Average words per entry: {total_words//total_entries if total_entries > 0 else 0}
        • Average mood while journaling: {avg_mood:.1f}/10
        • Days journaling: {date_range}
        """

class TherapeuticTechniques:
    def __init__(self):
        self.techniques = {
            'breathing': {
                'name': '4-7-8 Breathing Exercise',
                'description': 'A calming breathing technique to reduce anxiety',
                'instructions': [
                    'Sit comfortably and close your eyes',
                    'Exhale completely through your mouth',
                    'Inhale through your nose for 4 counts',
                    'Hold your breath for 7 counts',
                    'Exhale through your mouth for 8 counts',
                    'Repeat 3-4 times'
                ]
            },
            'grounding': {
                'name': '5-4-3-2-1 Grounding Technique',
                'description': 'Use your senses to ground yourself in the present',
                'instructions': [
                    'Name 5 things you can see',
                    'Name 4 things you can touch',
                    'Name 3 things you can hear',
                    'Name 2 things you can smell',
                    'Name 1 thing you can taste'
                ]
            },
            'progressive_relaxation': {
                'name': 'Progressive Muscle Relaxation',
                'description': 'Systematically tense and relax muscle groups',
                'instructions': [
                    'Start with your toes - tense for 5 seconds, then relax',
                    'Move to your calves - tense and relax',
                    'Continue with thighs, buttocks, abdomen',
                    'Tense and relax your hands, arms, shoulders',
                    'Finish with your face and head muscles',
                    'Take deep breaths throughout'
                ]
            },
            'thought_challenging': {
                'name': 'Thought Challenging (CBT)',
                'description': 'Question and reframe negative thoughts',
                'instructions': [
                    'Identify the negative thought',
                    'Ask: Is this thought realistic?',
                    'What evidence supports/contradicts it?',
                    'What would you tell a friend in this situation?',
                    'Reframe the thought more positively',
                    'Practice the new thought'
                ]
            },
            'gratitude': {
                'name': 'Gratitude Practice',
                'description': 'Focus on positive aspects of your life',
                'instructions': [
                    'Think of 3 things you\'re grateful for today',
                    'Be specific about why you\'re grateful',
                    'Include small and large things',
                    'Feel the emotion of gratitude',
                    'Write them down if helpful',
                    'Practice daily for best results'
                ]
            }
        }
    
    def get_technique(self, technique_name):
        """Get a specific technique"""
        return self.techniques.get(technique_name)
    
    def suggest_technique(self, emotion):
        """Suggest a technique based on emotion"""
        suggestions = {
            'anxiety': ['breathing', 'grounding'],
            'stress': ['breathing', 'progressive_relaxation'],
            'depression': ['gratitude', 'thought_challenging'],
            'anger': ['breathing', 'progressive_relaxation'],
            'general': ['breathing', 'gratitude']
        }
        
        recommended = suggestions.get(emotion, suggestions['general'])
        return random.choice(recommended)

class MentalHealthChatbot:
    def __init__(self):
        self.load_models()
        self.empathetic_responses = self.load_empathetic_responses()
        self.crisis_keywords = [
            'suicide', 'kill myself', 'end it all', 'hurt myself', 'self harm',
            'want to die', 'better off dead', 'no point living', 'worthless'
        ]
        self.mood_tracker = MoodTracker()
        self.journal_manager = JournalManager()
        self.techniques = TherapeuticTechniques()
    
    @st.cache_resource
    def load_models(_self):
        """Load pre-trained models with caching"""
        try:
            # Use DialoGPT for conversational responses
            tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
            model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
            
            # Sentiment analysis for understanding emotional context
            sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            return {
                'tokenizer': tokenizer,
                'model': model,
                'sentiment_analyzer': sentiment_analyzer
            }
        except Exception as e:
            st.warning(f"Could not load AI models: {e}")
            st.info("Using simplified responses without AI models.")
            return None
    
    def load_empathetic_responses(self):
        """Load pre-defined empathetic responses for different emotional states"""
        return {
            'anxiety': [
                "I understand that anxiety can feel overwhelming. Remember that these feelings are temporary and you're stronger than you think.",
                "Anxiety is tough, but you're not alone in this. Have you tried any grounding techniques like deep breathing?",
                "It's completely normal to feel anxious sometimes. What usually helps you feel more calm and centered?"
            ],
            'depression': [
                "I hear that you're going through a difficult time. Your feelings are valid, and it's okay to not be okay sometimes.",
                "Depression can make everything feel harder. Please know that you matter and there are people who care about you.",
                "Thank you for sharing how you're feeling. Small steps forward are still progress, even when they don't feel like much."
            ],
            'stress': [
                "Stress can be really challenging to manage. What's been weighing on your mind lately?",
                "It sounds like you're dealing with a lot right now. Remember that it's okay to take things one step at a time.",
                "Stress affects everyone differently. Have you been able to find any moments of peace or relaxation recently?"
            ],
            'loneliness': [
                "Feeling lonely is one of the most human experiences there is. You're not as alone as you might feel right now.",
                "Loneliness can be really painful. Is there anyone in your life you feel comfortable reaching out to?",
                "I'm here to listen. Sometimes talking about loneliness can help it feel a little less overwhelming."
            ],
            'anger': [
                "It sounds like you're feeling really frustrated or angry about something. Those feelings are completely valid.",
                "Anger can be a sign that something important to you has been threatened or hurt. What's behind these feelings?",
                "It's okay to feel angry. Let's talk about what's triggering these emotions and how we can work through them."
            ],
            'general': [
                "Thank you for sharing that with me. How are you feeling about everything right now?",
                "I appreciate you opening up. What would be most helpful for you in this moment?",
                "It takes courage to talk about difficult feelings. What kind of support are you looking for today?"
            ]
        }
    
    def detect_crisis(self, text):
        """Detect potential crisis situations"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.crisis_keywords)
    
    def analyze_sentiment_and_emotion(self, text):
        """Analyze sentiment and detect emotional context"""
        models = self.load_models()
        if not models:
            # Fallback to simple keyword detection
            text_lower = text.lower()
            emotion_keywords = {
                'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'overwhelmed', 'scared'],
                'depression': ['sad', 'depressed', 'hopeless', 'empty', 'numb', 'worthless'],
                'stress': ['stressed', 'pressure', 'exhausted', 'tired', 'burned out'],
                'loneliness': ['lonely', 'alone', 'isolated', 'disconnected', 'abandoned'],
                'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'annoyed']
            }
            
            detected_emotion = 'general'
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_emotion = emotion
                    break
            
            return detected_emotion, 0.7
        
        try:
            # Get sentiment scores
            sentiment_results = models['sentiment_analyzer'](text)
            
            # Detect emotional keywords
            text_lower = text.lower()
            emotion_keywords = {
                'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'overwhelmed', 'scared'],
                'depression': ['sad', 'depressed', 'hopeless', 'empty', 'numb', 'worthless'],
                'stress': ['stressed', 'pressure', 'exhausted', 'tired', 'burned out'],
                'loneliness': ['lonely', 'alone', 'isolated', 'disconnected', 'abandoned'],
                'anger': ['angry', 'furious', 'mad', 'irritated', 'frustrated', 'annoyed']
            }
            
            detected_emotion = 'general'
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_emotion = emotion
                    break
            
            # Get confidence from sentiment analysis
            confidence = max([score['score'] for score in sentiment_results[0]])
            
            return detected_emotion, confidence
            
        except Exception as e:
            st.warning(f"Error in sentiment analysis: {e}")
            return 'general', 0.5
    
    def generate_empathetic_response(self, user_input, emotion, confidence):
        """Generate empathetic response based on emotion and context"""
        
        # Check for crisis keywords first
        if self.detect_crisis(user_input):
            return self.get_crisis_response()
        
        # Get appropriate empathetic response
        responses = self.empathetic_responses.get(emotion, self.empathetic_responses['general'])
        base_response = random.choice(responses)
        
        # Suggest a therapeutic technique
        suggested_technique = self.techniques.suggest_technique(emotion)
        technique_suggestion = f"\n\n💡 **Technique Suggestion**: Try the {self.techniques.get_technique(suggested_technique)['name']} - it might help with what you're experiencing."
        
        return base_response + technique_suggestion
    
    def get_crisis_response(self):
        """Provide crisis intervention response"""
        return """
        🚨 I'm concerned about what you've shared. Please know that you're not alone and help is available:

        **Immediate Help:**
        • National Suicide Prevention Lifeline: AASRA : 📞 +91-98204-66726
        • Emergency Services: 📞 1800-599-0019

        **You matter, and your life has value.** Please consider reaching out to a mental health professional or someone you trust.
        
        Is there someone you can call right now? I'm here to talk, but professional help might be what you need most.
        """

def main():
    # Initialize components
    if 'chatbot' not in st.session_state:
        try:
            st.session_state.chatbot = MentalHealthChatbot()
        except Exception as e:
            st.error(f"Error initializing chatbot: {e}")
            st.info("Please refresh the page or try again later.")
            return
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'chat'
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🧠 MindCare Pro - Advanced Mental Health Support</h1>
        <p>Chat • Mood Tracking • Journaling • Therapeutic Techniques</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["💬 Chat", "📊 Mood Tracker", "📝 Journal", "🧘 Techniques", "📈 Insights"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        mood_tracker_interface()
    
    with tab3:
        journal_interface()
    
    with tab4:
        techniques_interface()
    
    with tab5:
        insights_interface()

def chat_interface():
    """Main chat interface"""
    
    # Only use sidebar if not already being used by user dashboard
    if not st.session_state.get('user_authenticated', False):
        # Sidebar with resources
        with st.sidebar:
            st.markdown("### 📋 Resources & Information")
            
            st.markdown("""
            <div class="emergency-notice">
                <h4>🆘 Crisis Resources</h4>
                <p><strong>National Suicide Prevention Lifeline:</strong><br>988</p>
                <p><strong>Crisis Text Line:</strong><br>Text HOME to 741741</p>
                <p><strong>Emergency:</strong><br>📞 +91-98204-66726 </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick mood log
            st.markdown("### 😊 Quick Mood Check")
            col1, col2 = st.columns(2)
            with col1:
                mood_score = st.slider("Mood (1-10)", 1, 10, 5, key="quick_mood")
            with col2:
                if st.button("Log Mood", type="secondary"):
                    st.session_state.chatbot.mood_tracker.log_mood(mood_score, "general", "Quick check")
                    st.success("Mood logged!")
            
            if st.button("Clear Chat", type="secondary"):
                st.session_state.messages = []
                st.rerun()
    
    # Emergency notice
    st.markdown("""
    <div class="emergency-notice">
        <strong>⚠️ Important Notice:</strong> This chatbot is not a replacement for professional mental health care. 
        If you're experiencing a mental health crisis, please contact emergency services or a mental health professional immediately.
    </div>
    """, unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>MindCare:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_area(
            "How are you feeling today? What's on your mind?",
            key="user_input",
            height=100,
            placeholder="Share your thoughts and feelings here..."
        )
    
    with col2:
        st.write("")
        st.write("")
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Process user input
    if send_button and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            emotion, confidence = st.session_state.chatbot.analyze_sentiment_and_emotion(user_input)
            response = st.session_state.chatbot.generate_empathetic_response(user_input, emotion, confidence)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Initial greeting
    if len(st.session_state.messages) == 0:
        initial_message = """
        Hello! I'm MindCare Pro, your comprehensive mental health support companion. I'm here to listen, provide support, and help you with various tools for mental wellness.
        
        **What I can help you with:**
        • 💬 Supportive conversations and emotional support
        • 📊 Mood tracking and insights
        • 📝 Guided journaling
        • 🧘 Therapeutic techniques and exercises
        
        Remember, while I can offer support and coping strategies, I'm not a replacement for professional mental health care.
        
        How are you feeling today? What would you like to explore?
        """
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        st.rerun()

def mood_tracker_interface():
    """Mood tracking interface"""
    st.header("📊 Mood Tracker")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Log Your Mood")
        
        mood_score = st.slider("How are you feeling? (1-10)", 1, 10, 5, key="mood_slider")
        
        emotion = st.selectbox("Primary emotion:", 
                              ["happy", "sad", "anxious", "angry", "excited", "calm", "stressed", "lonely", "grateful", "frustrated"])
        
        notes = st.text_area("Notes (optional):", height=100, key="mood_notes")
        
        if st.button("Log Mood", type="primary"):
            st.session_state.chatbot.mood_tracker.log_mood(mood_score, emotion, notes)
            st.success("Mood logged successfully!")
            st.rerun()
    
    with col2:
        st.subheader("Mood Visualization")
        
        chart = st.session_state.chatbot.mood_tracker.create_mood_chart()
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Start logging your mood to see trends!")
        
        # Mood insights
        insights = st.session_state.chatbot.mood_tracker.get_mood_insights()
        st.markdown(insights)
    
    # Recent mood entries
    st.subheader("Recent Mood Entries")
    recent_data = st.session_state.chatbot.mood_tracker.get_mood_history(7)
    
    if not recent_data.empty:
        for _, entry in recent_data.tail(5).iterrows():
            mood_emoji = "😢" if entry['mood_score'] <= 3 else "😐" if entry['mood_score'] <= 6 else "😊"
            st.markdown(f"""
            <div class="mood-card">
                <strong>{mood_emoji} {entry['mood_score']}/10 - {entry['emotion'].title()}</strong><br>
                <small>{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}</small><br>
                {entry['notes'] if entry['notes'] else 'No notes'}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No mood entries yet. Start by logging your current mood!")

def journal_interface():
    """Journaling interface"""
    st.header("📝 Digital Journal")
    
    tab1, tab2, tab3 = st.tabs(["✍️ Write Entry", "📖 View Entries", "🔍 Search"])
    
    with tab1:
        st.subheader("New Journal Entry")
        
        title = st.text_input("Entry Title:", key="journal_title")
        content = st.text_area("Write your thoughts...", height=200, key="journal_content")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            mood_score = st.slider("Mood while writing:", 1, 10, 5, key="journal_mood")
        with col2:
            tags_input = st.text_input("Tags (comma-separated):", key="journal_tags")
        with col3:
            st.write("")
            st.write("")
            if st.button("Save Entry", type="primary"):
                if title and content:
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                    entry_id = st.session_state.chatbot.journal_manager.add_entry(title, content, mood_score, tags)
                    st.success(f"Journal entry saved! (ID: {entry_id})")
                    
                    # Clear form
                    st.session_state.journal_title = ""
                    st.session_state.journal_content = ""
                    st.session_state.journal_tags = ""
                    st.rerun()
                else:
                    st.error("Please fill in both title and content.")
    
    with tab2:
        st.subheader("Your Journal Entries")
        
        entries = st.session_state.chatbot.journal_manager.get_entries(10)
        
        if entries:
            for entry in entries:
                mood_emoji = "😢" if entry['mood_score'] <= 3 else "😐" if entry['mood_score'] <= 6 else "😊"
                
                st.markdown(f"""
                <div class="journal-entry">
                    <h4>{mood_emoji} {entry['title']}</h4>
                    <small>{entry['timestamp'].strftime('%Y-%m-%d %H:%M')} | Mood: {entry['mood_score']}/10 | Words: {entry['word_count']}</small>
                    <p>{entry['content'][:200]}{'...' if len(entry['content']) > 200 else ''}</p>
                    <p><strong>Tags:</strong> {', '.join(entry['tags']) if entry['tags'] else 'None'}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No journal entries yet. Start writing your first entry!")
        
        # Journal statistics
        stats = st.session_state.chatbot.journal_manager.get_journal_stats()
        st.markdown(stats)
    
    with tab3:
        st.subheader("Search Journal Entries")
        
        search_query = st.text_input("Search for:", key="journal_search")
        
        if search_query:
            results = st.session_state.chatbot.journal_manager.search_entries(search_query)
            
            if results:
                st.success(f"Found {len(results)} entries:")
                for entry in results:
                    mood_emoji = "😢" if entry['mood_score'] <= 3 else "😐" if entry['mood_score'] <= 6 else "😊"
                    
                    st.markdown(f"""
                    <div class="journal-entry">
                        <h4>{mood_emoji} {entry['title']}</h4>
                        <small>{entry['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
                        <p>{entry['content'][:150]}{'...' if len(entry['content']) > 150 else ''}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No entries found matching your search.")

def techniques_interface():
    """Therapeutic techniques interface"""
    st.header("🧘 Therapeutic Techniques")
    
    st.markdown("Explore various evidence-based techniques to help manage stress, anxiety, and other mental health challenges.")
    
    # Technique selection
    technique_names = list(st.session_state.chatbot.techniques.techniques.keys())
    technique_display = {
        'breathing': '🫁 4-7-8 Breathing Exercise',
        'grounding': '🌍 5-4-3-2-1 Grounding Technique',
        'progressive_relaxation': '💆 Progressive Muscle Relaxation',
        'thought_challenging': '🧠 Thought Challenging (CBT)',
        'gratitude': '🙏 Gratitude Practice'
    }
    
    selected_technique = st.selectbox(
        "Choose a technique:",
        technique_names,
        format_func=lambda x: technique_display[x]
    )
    
    # Display technique
    technique = st.session_state.chatbot.techniques.get_technique(selected_technique)
    
    if technique:
        st.markdown(f"""
        <div class="technique-card">
            <h3>{technique['name']}</h3>
            <p><strong>Description:</strong> {technique['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Instructions:")
        for i, instruction in enumerate(technique['instructions'], 1):
            st.markdown(f"{i}. {instruction}")
        
        # Guided practice timer
        if selected_technique == 'breathing':
            st.subheader("🕐 Guided Practice Timer")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Start 4-7-8 Breathing", type="primary"):
                    st.session_state.breathing_active = True
            with col2:
                cycles = st.number_input("Number of cycles:", min_value=1, max_value=10, value=4)
            with col3:
                if st.button("Stop"):
                    st.session_state.breathing_active = False
            
            if st.session_state.get('breathing_active', False):
                breathing_exercise(cycles)
        
        elif selected_technique == 'grounding':
            st.subheader("🌍 Interactive Grounding Exercise")
            grounding_exercise()
        
        elif selected_technique == 'gratitude':
            st.subheader("🙏 Gratitude Journal")
            gratitude_exercise()

def breathing_exercise(cycles):
    """Interactive breathing exercise"""
    st.markdown("### Follow the breathing pattern below:")
    
    phases = ['Inhale (4 counts)', 'Hold (7 counts)', 'Exhale (8 counts)']
    phase_durations = [4, 7, 8]
    
    placeholder = st.empty()
    
    for cycle in range(cycles):
        st.write(f"**Cycle {cycle + 1} of {cycles}**")
        
        for phase, duration in zip(phases, phase_durations):
            for count in range(duration, 0, -1):
                placeholder.markdown(f"## {phase}: {count}")
                time.sleep(1)
        
        placeholder.markdown("**Rest for 2 seconds...**")
        time.sleep(2)
    
    placeholder.markdown("## ✅ Breathing exercise complete!")
    st.success("Great job! How do you feel now?")
    st.session_state.breathing_active = False

def grounding_exercise():
    """Interactive grounding exercise"""
    grounding_steps = [
        "Name 5 things you can see around you:",
        "Name 4 things you can touch:",
        "Name 3 things you can hear:",
        "Name 2 things you can smell:",
        "Name 1 thing you can taste:"
    ]
    
    if 'grounding_step' not in st.session_state:
        st.session_state.grounding_step = 0
    
    if st.session_state.grounding_step < len(grounding_steps):
        st.markdown(f"### Step {st.session_state.grounding_step + 1}")
        st.markdown(grounding_steps[st.session_state.grounding_step])
        
        user_response = st.text_area(f"Your response for step {st.session_state.grounding_step + 1}:", key=f"grounding_{st.session_state.grounding_step}")
        
        if st.button("Next Step", type="primary") and user_response:
            st.session_state.grounding_step += 1
            st.rerun()
    else:
        st.success("🎉 Grounding exercise complete! You've successfully connected with your present moment.")
        if st.button("Start Over"):
            st.session_state.grounding_step = 0
            st.rerun()

def gratitude_exercise():
    """Interactive gratitude exercise"""
    st.markdown("Write down three things you're grateful for today:")
    
    gratitude_1 = st.text_input("1. I'm grateful for:", key="gratitude_1")
    gratitude_2 = st.text_input("2. I'm grateful for:", key="gratitude_2")
    gratitude_3 = st.text_input("3. I'm grateful for:", key="gratitude_3")
    
    if st.button("Save Gratitude Entry", type="primary"):
        if gratitude_1 and gratitude_2 and gratitude_3:
            gratitude_entry = f"Today I'm grateful for:\n1. {gratitude_1}\n2. {gratitude_2}\n3. {gratitude_3}"
            
            # Save as journal entry
            st.session_state.chatbot.journal_manager.add_entry(
                f"Gratitude - {datetime.now().strftime('%Y-%m-%d')}",
                gratitude_entry,
                8,  # Gratitude typically correlates with higher mood
                ["gratitude", "daily practice"]
            )
            
            st.success("✅ Gratitude entry saved to your journal!")
            st.balloons()
        else:
            st.error("Please fill in all three gratitude items.")

def insights_interface():
    """Insights and analytics interface"""
    st.header("📈 Mental Health Insights")
    
    # Overall statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mood_data = st.session_state.chatbot.mood_tracker.get_mood_history(30)
        avg_mood = mood_data['mood_score'].mean() if not mood_data.empty else 0
        st.metric("30-Day Average Mood", f"{avg_mood:.1f}/10")
    
    with col2:
        journal_entries = len(st.session_state.journal_entries)
        st.metric("Total Journal Entries", journal_entries)
    
    with col3:
        chat_messages = len([msg for msg in st.session_state.messages if msg['role'] == 'user'])
        st.metric("Chat Interactions", chat_messages)
    
    # Mood trends
    st.subheader("📊 Detailed Mood Analysis")
    
    mood_chart = st.session_state.chatbot.mood_tracker.create_mood_chart()
    if mood_chart:
        st.plotly_chart(mood_chart, use_container_width=True)
        
        # Emotion distribution
        if not mood_data.empty:
            emotion_counts = mood_data['emotion'].value_counts()
            fig_pie = px.pie(
                values=emotion_counts.values, 
                names=emotion_counts.index,
                title="Emotion Distribution (Past 30 Days)"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Start tracking your mood to see detailed insights!")
    
    # Weekly summary
    st.subheader("📅 Weekly Summary")
    
    if not mood_data.empty:
        weekly_data = mood_data.groupby(mood_data['timestamp'].dt.date).agg({
            'mood_score': 'mean',
            'emotion': lambda x: x.mode().iloc[0] if not x.empty else 'unknown'
        }).tail(7)
        
        st.markdown("**Past 7 Days:**")
        for date, row in weekly_data.iterrows():
            mood_emoji = "😢" if row['mood_score'] <= 3 else "😐" if row['mood_score'] <= 6 else "😊"
            st.markdown(f"• {date}: {mood_emoji} {row['mood_score']:.1f}/10 - {row['emotion'].title()}")
    
    # Recommendations
    st.subheader("💡 Personalized Recommendations")
    
    recommendations = generate_recommendations()
    for rec in recommendations:
        st.markdown(f"• {rec}")

def generate_recommendations():
    """Generate personalized recommendations based on user data"""
    recommendations = []
    
    # Analyze mood data
    mood_data = st.session_state.chatbot.mood_tracker.get_mood_history(7)
    
    if not mood_data.empty:
        avg_mood = mood_data['mood_score'].mean()
        
        if avg_mood < 4:
            recommendations.append("Your mood has been lower recently. Consider scheduling time for activities you enjoy.")
            recommendations.append("Try the gratitude practice technique - it can help shift focus to positive aspects.")
        elif avg_mood > 7:
            recommendations.append("Great job maintaining positive mood! Keep up the good habits.")
        
        # Check for mood variability
        mood_std = mood_data['mood_score'].std()
        if mood_std > 2:
            recommendations.append("Your mood has been fluctuating. The 4-7-8 breathing technique might help with stability.")
    
    # Check journaling frequency
    journal_entries = len(st.session_state.journal_entries)
    if journal_entries == 0:
        recommendations.append("Consider starting a journal - it's a great way to process thoughts and emotions.")
    elif journal_entries > 0:
        recent_entries = [e for e in st.session_state.journal_entries 
                         if (datetime.now() - e['timestamp']).days <= 7]
        if len(recent_entries) == 0:
            recommendations.append("You haven't journaled recently. Try writing about your week!")
    
    # Default recommendations
    if not recommendations:
        recommendations = [
            "Keep exploring different therapeutic techniques to find what works best for you.",
            "Regular mood tracking can help you identify patterns and triggers.",
            "Remember that mental health is a journey - be patient and kind with yourself."
        ]
    
    return recommendations

if __name__ == "__main__":
    main()