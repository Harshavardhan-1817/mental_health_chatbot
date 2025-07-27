# user_interface.py
import streamlit as st
from datetime import datetime
import json

class UserInterface:
    def show_profile(self, username):
        """Display and manage user profile"""
        st.header(f"Profile: {username}")
        
        # Initialize user data if not exists
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
            
        if username not in st.session_state.user_data:
            st.session_state.user_data[username] = {
                'email': '',
                'age': 25,
                'emergency_contact': '',
                'therapist_info': '',
                'medications': '',
                'preferences': {
                    'notifications': True,
                    'data_sharing': False,
                    'reminder_frequency': 'Weekly'
                }
            }
        
        user_data = st.session_state.user_data[username]
        
        # Profile Information
        st.subheader("Personal Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input("Email", value=user_data.get('email', ''))
            age = st.number_input("Age", min_value=13, max_value=100, value=user_data.get('age', 25))
            emergency_contact = st.text_input("Emergency Contact", value=user_data.get('emergency_contact', ''))
        
        with col2:
            therapist_info = st.text_area("Therapist/Doctor Info", value=user_data.get('therapist_info', ''))
            medications = st.text_area("Current Medications", value=user_data.get('medications', ''))
        
        # Preferences
        st.subheader("Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            notifications = st.checkbox("Enable Notifications", value=user_data.get('preferences', {}).get('notifications', True))
            data_sharing = st.checkbox("Allow Anonymous Data Sharing for Research", value=user_data.get('preferences', {}).get('data_sharing', False))
        
        with col2:
            reminder_freq = st.selectbox(
                "Assessment Reminder Frequency",
                ["Daily", "Weekly", "Monthly", "Never"],
                index=["Daily", "Weekly", "Monthly", "Never"].index(user_data.get('preferences', {}).get('reminder_frequency', 'Weekly'))
            )
        
        # Save button
        if st.button("Save Profile", type="primary"):
            st.session_state.user_data[username] = {
                'email': email,
                'age': age,
                'emergency_contact': emergency_contact,
                'therapist_info': therapist_info,
                'medications': medications,
                'preferences': {
                    'notifications': notifications,
                    'data_sharing': data_sharing,
                    'reminder_frequency': reminder_freq
                }
            }
            st.success("Profile updated successfully!")
        
        # Export data option
        st.subheader("Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export My Data"):
                self.export_user_data(username)
        
        with col2:
            if st.button("Delete Account", type="secondary"):
                if st.checkbox("I understand this action cannot be undone"):
                    self.delete_user_account(username)
    
    def export_user_data(self, username):
        """Export user data as JSON"""
        export_data = {
            'username': username,
            'profile': st.session_state.user_data.get(username, {}),
            'test_results': [r for r in st.session_state.test_results if r.get('user') == username],
            'export_date': datetime.now().isoformat()
        }
        
        st.download_button(
            label="Download Data (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name=f"{username}_mental_health_data.json",
            mime="application/json"
        )
    
    def delete_user_account(self, username):
        """Delete user account and all associated data"""
        # Remove user data
        if username in st.session_state.user_data:
            del st.session_state.user_data[username]
        
        # Remove test results
        st.session_state.test_results = [
            r for r in st.session_state.test_results 
            if r.get('user') != username
        ]
        
        # Logout user
        st.session_state.user_logged_in = False
        st.session_state.current_user = None
        st.session_state.page = 'login'
        
        st.success("Account deleted successfully.")
        st.rerun()