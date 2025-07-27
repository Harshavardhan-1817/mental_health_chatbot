import streamlit as st
st.set_page_config(
    page_title="MindCare Pro - Mental Health Support",
    page_icon="🧠",
    layout="wide"
)

from user_integrated import check_user_authentication
from mental_health_bot import main as mindcare_main

def run_app():
    # User authentication and onboarding
    if check_user_authentication():
        mindcare_main()

if __name__ == "__main__":
    run_app()