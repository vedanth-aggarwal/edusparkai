# Streamlit-based UI Code
import streamlit as st
from typing import Dict
from rubric_generator.tools import RUBRIC
import base64

# Streamlit app setup
st.title("RUBRIC Generator Tool")

# Form for user input
with st.form("rubric_form"):
    grade = st.text_input("Enter Grade")
    points = st.text_input("Enter Points")
    standard = st.text_input("Enter Standard")
    assignment_url = st.text_input("Enter Assignment URL")
    file = st.file_uploader("Upload a file (optional)", type=["pdf", "docx", "txt"])

    # Form submit button
    submitted = st.form_submit_button("Generate RUBRIC")

if submitted:
    try:
        # Check if required inputs are provided
        if not grade or not assignment_url or not points or not standard:
            st.error("All input fields (grade, points, standard, and assignment URL) are required.")
        else:
            # Initialize the RUBRIC generator and run it
            gen = RUBRIC(grade, points, standard, assignment_url)
            result = gen.run()

            # Display result and generated PDF
            pdf_file = "dynamic_rubric.pdf"
            with open(pdf_file, "rb") as file:
                st.success("RUBRIC generated successfully!")
                pdf_data = file.read()
                
                # Embed PDF for display
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

    except Exception as e:
        error_message = f"Error in execution: {e}"
        st.error(error_message)
