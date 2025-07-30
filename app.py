import streamlit as st
st.set_page_config(
    page_title="MindCare Pro - Mental Health Support",
    page_icon="🧠",
    layout="wide"
)

from user_integrated import check_user_authentication
from mental_health_bot import main as mindcare_main

def run_app():
    try:
        # User authentication and onboarding
        if check_user_authentication():
            st.info("Loading MindCare Pro...")
            mindcare_main()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please refresh the page or try again later.")
        st.exception(e)
        
        # Fallback: Show a simple interface
        st.markdown("## 🧠 MindCare Pro - Fallback Mode")
        st.write("The main app encountered an error. Here's a simple interface:")
        
        st.subheader("Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Take Depression Test Again"):
                st.session_state.assessment_completed = False
                st.rerun()
        with col2:
            if st.button("Logout"):
                st.session_state.user_authenticated = False
                st.rerun()

if __name__ == "__main__":
    run_app()