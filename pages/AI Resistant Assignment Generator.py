import streamlit as st
import os
import base64
from ai_resistant_assignment_generator.tools import AIRAG

# Function to save uploaded file temporarily
def save_uploaded_file(uploaded_file):
    """Saves an uploaded file to a temporary location."""
    temp_path = os.path.join("temp_uploads", uploaded_file.name)
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

# Streamlit app title and description
st.title("AI-Resistant Assignment Generator")
st.write("Generate AI-resistant assignments by providing the necessary inputs.")

# Form for user input
with st.form("executor_form"):
    grade = st.text_input("Enter Grade", placeholder="e.g., 5th Grade")
    #assignment = st.text_area("Enter Assignment Details", placeholder="Describe the assignment requirements")
    assignment = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])
    description = st.text_area("Enter Additional Description (optional)", placeholder="Add any extra notes")
    # Form submit button
    submitted = st.form_submit_button("Generate Assignment")

if submitted:
    if not grade or not assignment:
        st.error("Missing required parameters: 'Grade' and 'Assignment' are mandatory.")
    else:
        try:
            os.makedirs("temp_uploads", exist_ok=True)
            saved_file_path = save_uploaded_file(assignment)
            # Create an instance of the AIRAG class and run the tool
            gen = AIRAG(grade, saved_file_path, description)
            result = gen.run()

            # Display the result in Streamlit
            st.success("Assignment generated successfully!")
            st.json(result)

        except Exception as e:
            error_message = f"Error in execution: {e}"
            st.error(error_message)
