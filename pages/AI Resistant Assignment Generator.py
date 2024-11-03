import streamlit as st
from app.services.logger import setup_logger
from app.features.ai_resistant_assignment_generator.tools import AIRAG
from app.services.schemas import AIRAGRequest
import json

# Initialize the logger
logger = setup_logger(__name__)

# Streamlit app title and description
st.title("AI-Resistant Assignment Generator")
st.write("Generate AI-resistant assignments by providing the necessary inputs.")

# Form for user input
with st.form("executor_form"):
    grade = st.text_input("Enter Grade", placeholder="e.g., 5th Grade")
    assignment = st.text_area("Enter Assignment Details", placeholder="Describe the assignment requirements")
    description = st.text_area("Enter Additional Description (optional)", placeholder="Add any extra notes")

    # Form submit button
    submitted = st.form_submit_button("Generate Assignment")

if submitted:
    if not grade or not assignment:
        st.error("Missing required parameters: 'Grade' and 'Assignment' are mandatory.")
    else:
        try:
            # Create an instance of the AIRAG class and run the tool
            gen = AIRAG(grade, assignment, description)
            result = gen.run()

            # Display the result in Streamlit
            st.success("Assignment generated successfully!")
            st.json(result)

        except Exception as e:
            error_message = f"Error in execution: {e}"
            logger.error(error_message)
            st.error(error_message)
