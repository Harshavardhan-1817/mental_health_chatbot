import streamlit as st
import json
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import uuid

class DepressionAssessment:
    """PHQ-9 Depression Assessment Tool"""
    
    def __init__(self):
        self.questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
        ]
        
        self.response_options = {
            0: "Not at all",
            1: "Several days",
            2: "More than half the days",
            3: "Nearly every day"
        }
        
        self.severity_levels = {
            (0, 4): {"level": "Minimal", "color": "#28a745", "description": "Minimal depression symptoms"},
            (5, 9): {"level": "Mild", "color": "#ffc107", "description": "Mild depression symptoms"},
            (10, 14): {"level": "Moderate", "color": "#fd7e14", "description": "Moderate depression symptoms"},
            (15, 19): {"level": "Moderately Severe", "color": "#dc3545", "description": "Moderately severe depression symptoms"},
            (20, 27): {"level": "Severe", "color": "#721c24", "description": "Severe depression symptoms"}
        }
    
    def get_severity_info(self, score: int) -> Dict:
        """Get severity information based on score"""
        for (min_score, max_score), info in self.severity_levels.items():
            if min_score <= score <= max_score:
                return {**info, "score": score}
        return {"level": "Unknown", "color": "#6c757d", "description": "Score out of range", "score": score}
    
    def get_recommendations(self, score: int) -> List[str]:
        """Get recommendations based on depression score"""
        severity = self.get_severity_info(score)
        
        recommendations = {
            "Minimal": [
                "Continue with your current self-care practices",
                "Regular exercise and social connections are great for maintaining mental health",
                "Consider journaling to track your mood patterns",
                "Practice gratitude exercises daily"
            ],
            "Mild": [
                "Try incorporating more physical activity into your routine",
                "Consider talking to a counselor or therapist",
                "Practice stress-reduction techniques like meditation",
                "Maintain regular sleep and eating schedules",
                "Stay connected with supportive friends and family"
            ],
            "Moderate": [
                "It's recommended to speak with a mental health professional",
                "Consider therapy (CBT has shown great results for depression)",
                "Regular exercise can be as effective as medication for mild-moderate depression",
                "Practice mindfulness and stress-reduction techniques",
                "Avoid alcohol and drugs as they can worsen symptoms"
            ],
            "Moderately Severe": [
                "Please consider seeing a mental health professional soon",
                "A combination of therapy and medication may be helpful",
                "Reach out to trusted friends, family, or support groups",
                "Create a safety plan if you're having thoughts of self-harm",
                "Consider intensive outpatient programs if available"
            ],
            "Severe": [
                "Please seek professional help immediately",
                "Contact a mental health crisis line if needed",
                "Consider inpatient treatment if you're having suicidal thoughts",
                "Inform a trusted person about how you're feeling",
                "Create a comprehensive safety plan with professional help"
            ]
        }
        
        return recommendations.get(severity["level"], ["Please consult with a mental health professional"])

class UserProfile:
    """Enhanced user profile with comprehensive tracking"""
    
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = datetime.now()
        self.last_login = datetime.now()
        
        # Assessment data
        self.depression_assessments = []
        self.anxiety_assessments = []
        
        # Personalized data
        self.goals = []
        self.achievements = []
        self.preferred_techniques = []
        self.crisis_contacts = []
        
        # Analytics
        self.mood_patterns = {}
        self.journal_insights = {}
        self.technique_usage = {}
        
        # Settings
        self.privacy_settings = {
            "share_anonymous_data": True,
            "emergency_contacts_enabled": True,
            "reminder_notifications": True
        }
    
    def add_depression_assessment(self, responses: List[int], additional_notes: str = ""):
        """Add a depression assessment result"""
        total_score = sum(responses)
        assessment = DepressionAssessment()
        severity_info = assessment.get_severity_info(total_score)
        
        assessment_data = {
            "timestamp": datetime.now(),
            "responses": responses,
            "total_score": total_score,
            "severity": severity_info["level"],
            "additional_notes": additional_notes,
            "recommendations": assessment.get_recommendations(total_score)
        }
        
        self.depression_assessments.append(assessment_data)
        return assessment_data
    
    def get_depression_history(self) -> pd.DataFrame:
        """Get depression assessment history as DataFrame"""
        if not self.depression_assessments:
            return pd.DataFrame()
        
        data = []
        for assessment in self.depression_assessments:
            data.append({
                'date': assessment['timestamp'].date(),
                'score': assessment['total_score'],
                'severity': assessment['severity'],
                'timestamp': assessment['timestamp']
            })
        
        return pd.DataFrame(data)
    
    def get_progress_insights(self) -> Dict:
        """Generate progress insights"""
        insights = {
            "total_assessments": len(self.depression_assessments),
            "days_active": (datetime.now() - self.created_at).days,
            "improvement_trend": "stable",
            "risk_factors": [],
            "positive_indicators": []
        }
        
        if len(self.depression_assessments) >= 2:
            recent_score = self.depression_assessments[-1]["total_score"]
            previous_score = self.depression_assessments[-2]["total_score"]
            
            if recent_score < previous_score - 2:
                insights["improvement_trend"] = "improving"
                insights["positive_indicators"].append("Depression scores are decreasing")
            elif recent_score > previous_score + 2:
                insights["improvement_trend"] = "concerning"
                insights["risk_factors"].append("Depression scores are increasing")
        
        return insights
    
    def set_goals(self, goals: List[str]):
        """Set personal mental health goals"""
        self.goals = []
        for goal in goals:
            self.goals.append({
                "id": str(uuid.uuid4()),
                "goal": goal,
                "created_at": datetime.now(),
                "completed": False,
                "progress": 0
            })
    
    def update_goal_progress(self, goal_id: str, progress: int):
        """Update progress on a specific goal"""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["progress"] = min(100, max(0, progress))
                if progress >= 100:
                    goal["completed"] = True
                    self.achievements.append({
                        "type": "goal_completed",
                        "description": f"Completed goal: {goal['goal']}",
                        "timestamp": datetime.now()
                    })
                break

class UserManager:
    """Enhanced user management system"""
    
    def __init__(self):
        if 'users_db' not in st.session_state:
            st.session_state.users_db = {}
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'user_authenticated' not in st.session_state:
            st.session_state.user_authenticated = False
    
    def hash_password(self, password: str) -> str:
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str) -> bool:
        """Create a new user account"""
        if username in st.session_state.users_db:
            return False
        
        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)
        
        # Store authentication data
        st.session_state.users_db[username] = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now()
        }
        
        # Create user profile
        profile = UserProfile(user_id, username, email)
        st.session_state[f"profile_{user_id}"] = profile
        
        return True
    
    def authenticate_user(self, username: str, password: str) -> bool:
        """Authenticate user login"""
        if username not in st.session_state.users_db:
            return False
        
        user_data = st.session_state.users_db[username]
        password_hash = self.hash_password(password)
        
        if user_data["password_hash"] == password_hash:
            st.session_state.current_user = user_data["user_id"]
            st.session_state.user_authenticated = True
            
            # Update last login
            profile = self.get_current_user_profile()
            if profile:
                profile.last_login = datetime.now()
            
            return True
        
        return False
    
    def get_current_user_profile(self) -> Optional[UserProfile]:
        """Get current user's profile"""
        if not st.session_state.user_authenticated or not st.session_state.current_user:
            return None
        
        return st.session_state.get(f"profile_{st.session_state.current_user}")
    
    def logout_user(self):
        """Logout current user"""
        st.session_state.user_authenticated = False
        st.session_state.current_user = None
    
    def is_new_user(self) -> bool:
        """Check if current user is new (less than 1 day old)"""
        profile = self.get_current_user_profile()
        if not profile:
            return False
        
        return (datetime.now() - profile.created_at).days == 0

def render_login_page():
    """Render login/registration page"""
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Welcome to MindCare Pro</h1>
        <p>Your Personal Mental Health Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    user_manager = UserManager()
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                if user_manager.authenticate_user(login_username, login_password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col2:
            if st.button("Demo Mode", type="secondary", use_container_width=True):
                # Create a demo user
                demo_id = "demo_" + str(uuid.uuid4())[:8]
                st.session_state.current_user = demo_id
                st.session_state.user_authenticated = True
                st.session_state[f"profile_{demo_id}"] = UserProfile(demo_id, "Demo User", "demo@example.com")
                st.success("Entered demo mode!")
                st.rerun()
    
    with tab2:
        st.subheader("Create New Account")
        
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        if st.button("Register", type="primary", use_container_width=True):
            if not all([reg_username, reg_email, reg_password, reg_password_confirm]):
                st.error("Please fill in all fields")
            elif reg_password != reg_password_confirm:
                st.error("Passwords don't match")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters")
            elif user_manager.create_user(reg_username, reg_email, reg_password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists")

def render_depression_assessment():
    """Render depression assessment for new users"""
    st.header("📋 Initial Mental Health Assessment")
    
    st.markdown("""
    <div class="emergency-notice">
        <strong>Welcome!</strong> To provide you with personalized support, we'd like you to complete 
        this brief mental health assessment. This will help us understand your current state and 
        provide tailored recommendations.
    </div>
    """, unsafe_allow_html=True)
    
    assessment = DepressionAssessment()
    user_manager = UserManager()
    profile = user_manager.get_current_user_profile()
    
    if not profile:
        st.error("User profile not found")
        return
    
    # Check if user has already completed assessment today
    today = datetime.now().date()
    recent_assessment = None
    if profile.depression_assessments:
        for assess in profile.depression_assessments:
            if assess["timestamp"].date() == today:
                recent_assessment = assess
                break
    
    if recent_assessment:
        st.success("✅ You've already completed today's assessment!")
        display_assessment_results(recent_assessment)
        
        if st.button("Take Assessment Again", type="secondary"):
            st.session_state.retake_assessment = True
            st.rerun()
        
        if not st.session_state.get('retake_assessment', False):
            if st.button("Continue to App", type="primary"):
                st.session_state.assessment_completed = True
                st.rerun()
            return
    
    # Display assessment form
    st.subheader("PHQ-9 Depression Screening")
    st.markdown("*Over the last 2 weeks, how often have you been bothered by any of the following problems?*")
    
    responses = []
    
    with st.form("depression_assessment"):
        for i, question in enumerate(assessment.questions):
            st.markdown(f"**{i+1}. {question}**")
            response = st.radio(
                f"Response for question {i+1}:",
                options=[0, 1, 2, 3],
                format_func=lambda x: assessment.response_options[x],
                key=f"q_{i}",
                horizontal=True
            )
            responses.append(response)
        
        additional_notes = st.text_area(
            "Additional notes or concerns (optional):",
            placeholder="Share any additional thoughts about your mental health..."
        )
        
        submitted = st.form_submit_button("Complete Assessment", type="primary")
    
    if submitted:
        # Save assessment
        assessment_result = profile.add_depression_assessment(responses, additional_notes)
        
        # Clear retake flag
        if 'retake_assessment' in st.session_state:
            del st.session_state.retake_assessment
        
        st.session_state.assessment_completed = True
        st.success("Assessment completed! Here are your results:")
        
        display_assessment_results(assessment_result)
        
        if st.button("Continue to MindCare Pro", type="primary"):
            st.rerun()

def display_assessment_results(assessment_result: Dict):
    """Display assessment results with recommendations"""
    assessment_tool = DepressionAssessment()
    severity_info = assessment_tool.get_severity_info(assessment_result["total_score"])
    
    # Results display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Your Score", f"{assessment_result['total_score']}/27")
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background-color: {severity_info['color']}; 
             color: white; border-radius: 10px;">
            <h3>{severity_info['level']}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"**Date:** {assessment_result['timestamp'].strftime('%Y-%m-%d %H:%M')}")
    
    # Recommendations
    st.subheader("📝 Personalized Recommendations")
    
    for i, recommendation in enumerate(assessment_result["recommendations"], 1):
        st.markdown(f"{i}. {recommendation}")
    
    # Crisis intervention if needed
    if assessment_result["total_score"] >= 15 or assessment_result["responses"][8] > 0:  # Question 9 is about self-harm
        st.markdown("""
        <div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 10px; padding: 1rem; margin: 1rem 0;">
            <h4>🚨 Important Resources</h4>
            <p><strong>If you're having thoughts of self-harm, please reach out for help immediately:</strong></p>
            <ul>
                <li><strong>National Suicide Prevention Lifeline:</strong> 988</li>
                <li><strong>Crisis Text Line:</strong> Text HOME to 741741</li>
                <li><strong>Emergency Services:</strong> 911</li>
            </ul>
            <p>Remember: You are not alone, and help is available.</p>
        </div>
        """, unsafe_allow_html=True)

def render_user_dashboard():
    """Render user dashboard with personalized insights"""
    user_manager = UserManager()
    profile = user_manager.get_current_user_profile()
    
    if not profile:
        st.error("User profile not found")
        return
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"## Welcome back, {profile.username}! 👋")
        days_active = (datetime.now() - profile.created_at).days
        st.markdown(f"*Member for {days_active} days*")
    
    with col2:
        if st.button("Assessment History", type="secondary"):
            st.session_state.show_assessment_history = True
    
    with col3:
        if st.button("Logout", type="secondary"):
            user_manager.logout_user()
            st.rerun()
    
    # Progress insights
    insights = profile.get_progress_insights()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assessments", insights["total_assessments"])
    
    with col2:
        st.metric("Days Active", insights["days_active"])
    
    with col3:
        trend_emoji = "📈" if insights["improvement_trend"] == "improving" else "📉" if insights["improvement_trend"] == "concerning" else "➡️"
        st.metric("Trend", f"{trend_emoji} {insights['improvement_trend'].title()}")
    
    with col4:
        if profile.depression_assessments:
            latest_score = profile.depression_assessments[-1]["total_score"]
            st.metric("Latest Score", f"{latest_score}/27")
    
    # Assessment history chart
    if profile.depression_assessments:
        st.subheader("📊 Your Progress Over Time")
        
        df = profile.get_depression_history()
        
        if not df.empty:
            fig = px.line(df, x='date', y='score', 
                         title='Depression Assessment Scores Over Time',
                         labels={'score': 'PHQ-9 Score', 'date': 'Date'})
            
            # Add severity level background colors
            fig.add_hrect(y0=0, y1=4, fillcolor="green", opacity=0.1, annotation_text="Minimal")
            fig.add_hrect(y0=5, y1=9, fillcolor="yellow", opacity=0.1, annotation_text="Mild")
            fig.add_hrect(y0=10, y1=14, fillcolor="orange", opacity=0.1, annotation_text="Moderate")
            fig.add_hrect(y0=15, y1=19, fillcolor="red", opacity=0.1, annotation_text="Mod. Severe")
            fig.add_hrect(y0=20, y1=27, fillcolor="darkred", opacity=0.1, annotation_text="Severe")
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Goals section
    st.subheader("🎯 Your Mental Health Goals")
    
    if not profile.goals:
        st.info("No goals set yet. Let's create some!")
        
        if st.button("Set Your First Goals"):
            st.session_state.setting_goals = True
    else:
        for goal in profile.goals:
            progress_color = "success" if goal["completed"] else "normal"
            st.progress(goal["progress"] / 100, text=f"{goal['goal']} ({goal['progress']}%)")
    
    # Goal setting interface
    if st.session_state.get('setting_goals', False):
        st.subheader("✨ Set Your Mental Health Goals")
        
        suggested_goals = [
            "Practice daily mindfulness for 10 minutes",
            "Exercise 3 times per week",
            "Journal every evening",
            "Get 8 hours of sleep nightly",
            "Connect with a friend weekly",
            "Practice gratitude daily",
            "Limit social media to 1 hour daily",
            "Try a new coping technique each week"
        ]
        
        selected_goals = st.multiselect(
            "Choose from suggested goals or write your own:",
            suggested_goals
        )
        
        custom_goal = st.text_input("Add a custom goal:")
        
        if custom_goal:
            selected_goals.append(custom_goal)
        
        if st.button("Save Goals") and selected_goals:
            profile.set_goals(selected_goals)
            st.session_state.setting_goals = False
            st.success("Goals saved successfully!")
            st.rerun()

def check_user_authentication():
    """Check if user is authenticated and handle new user flow"""
    user_manager = UserManager()
    
    # If not authenticated, show login page
    if not st.session_state.user_authenticated:
        render_login_page()
        return False
    
    # If authenticated but new user hasn't completed assessment
    if (user_manager.is_new_user() and 
        not st.session_state.get('assessment_completed', False)):
        render_depression_assessment()
        return False
    
    # Show user dashboard in sidebar
    with st.sidebar:
        render_user_dashboard()
    
    return True

# Export the main functions that will be used in the main app
__all__ = [
    'check_user_authentication',
    'UserManager', 
    'UserProfile', 
    'DepressionAssessment',
    'render_user_dashboard'
]