import os
import streamlit as st
from syllabus_generator.tools import (
    Syllabus_generator,
    Meme_generator_with_reddit,
    WordGenerator,
    PDFGenerator,
)

# Streamlit UI setup
st.title("Syllabus Generator and Content Creator")
st.write("Generate a syllabus, download it as a PDF/Word document, and view related memes.")

# Input form for the user
with st.form("syllabus_form"):
    grade = st.text_input("Enter Grade", placeholder="e.g., 5th Grade")
    subject = st.text_input("Enter Subject", placeholder="e.g., Mathematics")
    syllabus_type = st.text_input("Enter Syllabus Type", placeholder="e.g., Detailed")
    instructions = st.text_area("Enter Instructions (optional)", placeholder="e.g., Special topics to include")
    file = st.file_uploader("Upload a File (optional)")
    output_type = st.selectbox("Select Output Type", ["", "pdf", "word"], index=0)

    # Submit button
    submitted = st.form_submit_button("Generate Syllabus")

if submitted:
    if not grade or not subject:
        st.error("Both 'Grade' and 'Subject' are required.")
    else:
        try:
            content = file.read() if file else None  # Read file content if provided

            # Generate memes related to the subject
            Memes_Generator = Meme_generator_with_reddit(subject=subject)
            memes = Memes_Generator.get_memes()

            # Generate the syllabus
            Syllabus_Generator = Syllabus_generator(
                grade=grade,
                subject=subject,
                syllabus_type=syllabus_type,
                instructions=instructions,
                content=content,
                path="syllabus_generator/"
            )
            result = Syllabus_Generator.run()
            result['memes'] = memes

            # Handle specific output types: PDF or Word document
            if output_type == 'pdf':
                pdf_gen = PDFGenerator(grade, subject)
                pdf_file = pdf_gen.generate_pdf(result)
                st.success("PDF generated successfully!")
                st.download_button(
                    label="Download PDF",
                    data=pdf_file,
                    file_name=f"{grade}_{subject}_syllabus.pdf",
                    mime="application/pdf"
                )
            elif output_type == 'word':
                word_gen = WordGenerator(grade, subject)
                word_file = word_gen.generate_word(result)
                st.success("Word document generated successfully!")
                st.download_button(
                    label="Download Word Document",
                    data=word_file,
                    file_name=f"{grade}_{subject}_syllabus.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            else:
                st.json(result)

            # Display the memes in the UI
            st.write("Memes related to the subject:")
            for meme in memes:
                st.image(meme, caption="Meme")

        except Exception as e:
            error_message = f"Error in execution: {e}"
            st.error(error_message)