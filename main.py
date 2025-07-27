# main.py - Main application file
import streamlit as st
from depression_test import DepressionTest
from user_interface import UserInterface
import pandas as pd
import json
from datetime import datetime

class MentalHealthApp:
    def __init__(self):
        self.init_session_state()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'user_logged_in' not in st.session_state:
            st.session_state.user_logged_in = False
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'page' not in st.session_state:
            st.session_state.page = 'login'
        if 'test_results' not in st.session_state:
            st.session_state.test_results = []
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
    
    def login_page(self):
        """Simple login page"""
        st.title("Mental Health Assessment Platform")
        st.header("Login")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if username and password:  # Simple validation
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = username
                    st.session_state.page = 'dashboard'
                    st.rerun()
                else:
                    st.error("Please enter both username and password")
        
        with col2:
            if st.button("Sign Up"):
                st.session_state.page = 'signup'
                st.rerun()
    
    def signup_page(self):
        """Simple signup page"""
        st.title("Sign Up")
        
        username = st.text_input("Choose Username")
        password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        email = st.text_input("Email")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Account"):
                if username and password and password == confirm_password:
                    st.success("Account created successfully!")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error("Please fill all fields and ensure passwords match")
        
        with col2:
            if st.button("Back to Login"):
                st.session_state.page = 'login'
                st.rerun()
    
    def dashboard(self):
        """Main dashboard after login"""
        st.title(f"Welcome, {st.session_state.current_user}!")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        
        menu_options = ["Dashboard", "Take Depression Test", "View Results", "User Profile", "Resources"]
        choice = st.sidebar.selectbox("Go to", menu_options)
        
        if st.sidebar.button("Logout"):
            self.logout()
        
        # Main content based on selection
        if choice == "Dashboard":
            self.show_dashboard_content()
        elif choice == "Take Depression Test":
            self.show_depression_test()
        elif choice == "View Results":
            self.show_test_results()
        elif choice == "User Profile":
            self.show_user_profile()
        elif choice == "Resources":
            self.show_resources()
    
    def show_dashboard_content(self):
        """Dashboard overview"""
        st.header("Mental Health Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Tests Taken", len(st.session_state.test_results))
        
        with col2:
            if st.session_state.test_results:
                latest_score = st.session_state.test_results[-1].get('score', 0)
                st.metric("Latest Test Score", f"{latest_score}/27")
            else:
                st.metric("Latest Test Score", "No tests taken")
        
        with col3:
            if st.session_state.test_results:
                avg_score = sum(result.get('score', 0) for result in st.session_state.test_results) / len(st.session_state.test_results)
                st.metric("Average Score", f"{avg_score:.1f}/27")
            else:
                st.metric("Average Score", "No data")
        
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Take Depression Assessment", use_container_width=True):
                st.session_state.page = 'test'
                st.rerun()
        
        with col2:
            if st.button("View Progress", use_container_width=True):
                st.session_state.page = 'results'
                st.rerun()
        
        # Show recent results if available
        if st.session_state.test_results:
            st.subheader("Recent Test Results")
            recent_results = st.session_state.test_results[-3:]  # Last 3 results
            
            for i, result in enumerate(reversed(recent_results)):
                with st.expander(f"Test taken on {result.get('date', 'Unknown date')}"):
                    st.write(f"**Score:** {result.get('score', 0)}/27")
                    st.write(f"**Severity:** {result.get('severity', 'Unknown')}")
                    st.write(f"**Recommendation:** {result.get('recommendation', 'No recommendation')}")
    
    def show_depression_test(self):
        """Show the depression test interface"""
        depression_test = DepressionTest()
        result = depression_test.run_test()
        
        if result:
            # Store the result
            result['date'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            result['user'] = st.session_state.current_user
            st.session_state.test_results.append(result)
    
    def show_test_results(self):
        """Show historical test results and analytics"""
        st.header("Your Test Results & Progress")
        
        if not st.session_state.test_results:
            st.info("No test results available. Take your first depression assessment to see your progress here.")
            if st.button("Take Depression Test"):
                st.session_state.page = 'test'
                st.rerun()
            return
        
        # Results overview
        st.subheader("Results Overview")
        results_df = pd.DataFrame(st.session_state.test_results)
        
        # Progress chart
        if len(st.session_state.test_results) > 1:
            st.subheader("Progress Over Time")
            st.line_chart(results_df.set_index('date')['score'])
        
        # Detailed results
        st.subheader("Detailed Results")
        for i, result in enumerate(reversed(st.session_state.test_results)):
            with st.expander(f"Test #{len(st.session_state.test_results)-i} - {result.get('date', 'Unknown date')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Score:** {result.get('score', 0)}/27")
                    st.write(f"**Severity Level:** {result.get('severity', 'Unknown')}")
                
                with col2:
                    severity = result.get('severity', '').lower()
                    if 'minimal' in severity:
                        st.success("Minimal Depression")
                    elif 'mild' in severity:
                        st.warning("Mild Depression")
                    elif 'moderate' in severity:
                        st.warning("Moderate Depression")
                    elif 'severe' in severity:
                        st.error("Severe Depression")
                
                st.write("**Recommendations:**")
                st.write(result.get('recommendation', 'No specific recommendations available.'))
                
                if result.get('resources'):
                    st.write("**Suggested Resources:**")
                    for resource in result.get('resources', []):
                        st.write(f"• {resource}")
    
    def show_user_profile(self):
        """Show and edit user profile"""
        user_interface = UserInterface()
        user_interface.show_profile(st.session_state.current_user)
    
    def show_resources(self):
        """Show mental health resources"""
        st.header("Mental Health Resources")
        
        st.subheader("🆘 Crisis Resources")
        st.write("""
        **If you're in immediate danger or having thoughts of self-harm:**
        - **Emergency:** Call 911 (US) or your local emergency number
        - **National Suicide Prevention Lifeline:** 988 (US)
        - **Crisis Text Line:** Text HOME to 741741
        """)
        
        st.subheader("📞 Professional Help")
        st.write("""
        - **Psychology Today:** Find therapists in your area
        - **BetterHelp:** Online therapy platform
        - **Talkspace:** Text-based therapy
        - **Your primary care physician** can provide referrals
        """)
        
        st.subheader("📚 Self-Help Resources")
        st.write("""
        - **Mindfulness apps:** Headspace, Calm, Insight Timer
        - **Mood tracking:** Daylio, Moodpath
        - **Online CBT:** MindShift, Sanvello
        """)
        
        st.subheader("🏃‍♀️ Lifestyle Support")
        st.write("""
        - Regular exercise and physical activity
        - Maintaining a consistent sleep schedule
        - Connecting with friends and family
        - Limiting alcohol and avoiding drugs
        - Eating a balanced diet
        """)
    
    def logout(self):
        """Handle user logout"""
        st.session_state.user_logged_in = False
        st.session_state.current_user = None
        st.session_state.page = 'login'
        st.rerun()
    
    def run(self):
        """Main application runner"""
        # Route to appropriate page
        if not st.session_state.user_logged_in:
            if st.session_state.page == 'signup':
                self.signup_page()
            else:
                self.login_page()
        else:
            self.dashboard()

# Run the application
if __name__ == "__main__":
    app = MentalHealthApp()
    app.run()