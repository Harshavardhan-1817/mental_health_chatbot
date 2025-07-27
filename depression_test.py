# depression_test.py - Depression test module
import streamlit as st

class DepressionTest:
    def __init__(self):
        self.questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
        ]
        
        self.options = [
            "Not at all",
            "Several days", 
            "More than half the days",
            "Nearly every day"
        ]
    
    def run_test(self):
        """Run the depression test and return results"""
        st.header("PHQ-9 Depression Assessment")
        st.write("Over the last 2 weeks, how often have you been bothered by any of the following problems?")
        
        # Initialize scores in session state if not exists
        if 'depression_scores' not in st.session_state:
            st.session_state.depression_scores = [0] * len(self.questions)
        
        # Display questions
        scores = []
        for i, question in enumerate(self.questions):
            score = st.radio(
                f"{i+1}. {question}",
                options=list(range(4)),
                format_func=lambda x: self.options[x],
                key=f"q_{i}",
                index=st.session_state.depression_scores[i]
            )
            scores.append(score)
            st.session_state.depression_scores[i] = score
        
        # Calculate and show results
        if st.button("Submit Assessment", type="primary"):
            total_score = sum(scores)
            severity, recommendation, resources = self.interpret_score(total_score)
            
            # Display results
            st.subheader("Assessment Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Score", f"{total_score}/27")
                st.write(f"**Severity Level:** {severity}")
            
            with col2:
                if total_score <= 4:
                    st.success("Minimal Depression")
                elif total_score <= 9:
                    st.info("Mild Depression")
                elif total_score <= 14:
                    st.warning("Moderate Depression")
                elif total_score <= 19:
                    st.warning("Moderately Severe Depression")
                else:
                    st.error("Severe Depression")
            
            st.write("**Recommendations:**")
            st.write(recommendation)
            
            if resources:
                st.write("**Suggested Next Steps:**")
                for resource in resources:
                    st.write(f"• {resource}")
            
            # Return results for storage
            return {
                'score': total_score,
                'severity': severity,
                'recommendation': recommendation,
                'resources': resources,
                'individual_scores': scores
            }
        
        return None
    
    def interpret_score(self, score):
        """Interpret the PHQ-9 score and provide recommendations"""
        if score <= 4:
            severity = "Minimal Depression"
            recommendation = "Your scores suggest minimal depression. Continue with healthy lifestyle practices and monitor your mood."
            resources = [
                "Continue regular exercise and healthy sleep habits",
                "Practice stress management techniques",
                "Stay connected with friends and family"
            ]
        elif score <= 9:
            severity = "Mild Depression"
            recommendation = "Your scores suggest mild depression. Consider lifestyle changes and monitoring your symptoms."
            resources = [
                "Consider counseling or therapy",
                "Increase physical activity and social engagement",
                "Practice mindfulness or meditation",
                "Monitor symptoms over time"
            ]
        elif score <= 14:
            severity = "Moderate Depression"
            recommendation = "Your scores suggest moderate depression. It's recommended to seek professional help."
            resources = [
                "Schedule an appointment with a mental health professional",
                "Consider therapy (CBT, interpersonal therapy)",
                "Discuss treatment options with your doctor",
                "Join a support group"
            ]
        elif score <= 19:
            severity = "Moderately Severe Depression"
            recommendation = "Your scores suggest moderately severe depression. Professional treatment is strongly recommended."
            resources = [
                "Seek immediate professional help",
                "Consider both therapy and medication",
                "Involve trusted friends or family in your care",
                "Create a safety plan"
            ]
        else:
            severity = "Severe Depression"
            recommendation = "Your scores suggest severe depression. Immediate professional intervention is recommended."
            resources = [
                "Seek immediate professional help",
                "Consider intensive treatment options",
                "Contact crisis resources if needed",
                "Don't face this alone - reach out for support"
            ]
        
        return severity, recommendation, resources