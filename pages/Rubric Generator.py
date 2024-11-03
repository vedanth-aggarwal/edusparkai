# Streamlit-based UI Code
import streamlit as st
import os
import base64
from rubric_generator.tools import RUBRIC

# Function to save uploaded file temporarily
def save_uploaded_file(uploaded_file):
    """Saves an uploaded file to a temporary location."""
    temp_path = os.path.join("temp_uploads", uploaded_file.name)
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

# Streamlit app setup
st.title("RUBRIC Generator Tool")

# Form for user input
with st.form("rubric_form"):
    grade = st.text_input("Enter Grade")
    points = st.text_input("Enter Points")
    standard = st.text_input("Enter Standard")
    file = st.file_uploader("Upload a file (optional)", type=["pdf", "docx", "txt"])

    # Form submit button
    submitted = st.form_submit_button("Generate RUBRIC")

if submitted:
    try:
        # Check if required inputs are provided
        if not grade or not points or not standard or not file:
            st.error("All input fields (grade, points, standard, and assignment) are required.")
        else:
            os.makedirs("temp_uploads", exist_ok=True)
            saved_file_path = save_uploaded_file(file)

            # Initialize the RUBRIC generator and run it
            gen = RUBRIC(grade, points, standard, saved_file_path)
            result = gen.run()

            pdf_file = "dynamic_rubric.pdf"

            # Check if the PDF file exists and is not empty
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
                with open(pdf_file, "rb") as pdf:
                    st.success("RUBRIC generated successfully!")
                    pdf_data = pdf.read()

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
            else:
                st.error("Failed to generate PDF or the PDF file is empty.")
            st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

    except Exception as e:
        error_message = f"Error in execution: {e}"
        st.error(error_message)
