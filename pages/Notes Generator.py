import streamlit as st
from typing import Any, Dict, Optional
from notes_generator.tools import NotesGenerator
import os

def save_uploaded_file(uploaded_file):
    """Saves an uploaded file to a temporary location."""
    temp_path = os.path.join("temp_uploads", uploaded_file.name)
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

# Streamlit UI setup
st.title("Notes Generator")
st.write("Generate notes from an uploaded file or URL with customized PDF options.")

# Input form for the user
file = st.file_uploader("Upload a File")
file_url = st.text_input("Enter File URL (optional)")
orientation = st.selectbox("Select Page Orientation", ["portrait", "landscape"], index=0)
columns = st.selectbox("Select Number of Columns", [1, 2], index=0)

if st.button("Generate Notes"):
    try:
        #file_content = file.read() if file else None

        os.makedirs("temp_uploads", exist_ok=True)
        saved_file_path = save_uploaded_file(file)

        # Ensure at least one input source is provided
        notes_generator = NotesGenerator(
                model='llama-3.1-70b-versatile',
                notes_content=saved_file_path,
                orientation=orientation,
                columns=columns
            )

            # Run the notes generation process
        result = notes_generator.run()

            # Display results
        st.success("Notes generated successfully.")
        st.json(result)

    except ValueError as ve:
        st.error(f"Validation error: {ve}")
    except Exception as e:
        error_message = f"Error generating notes: {e}"
        st.error(error_message)
