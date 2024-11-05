import os
import streamlit as st
from syllabus_generator.tools import (
    Syllabus_generator,
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
    syllabus_type = st.text_input("Enter Syllabus Type", placeholder="e.g., exam-based, project based learning, etc.")
    instructions = st.text_area("Enter Instructions", placeholder="e.g., Special topics to include and detailed info")
    #file = st.file_uploader("Upload a File (optional)")
    output_type = st.selectbox("Select Output Type", ["", "pdf", "word"], index=0)

    # Submit button
    submitted = st.form_submit_button("Generate Syllabus")

if submitted:
    if not grade or not subject:
        st.error("Both 'Grade' and 'Subject' are required.")
    else:
        try:
            #content = file.read() if file else None  # Read file content if provided

            # Generate memes related to the subject

            # Generate the syllabus
            Syllabus_Generator = Syllabus_generator(
                grade=grade,
                subject=subject,
                syllabus_type=syllabus_type,
                instructions=instructions,
            )
            result = Syllabus_Generator.run()
            with st.expander("Course Description"):
                st.write(result['course_description'])
            with st.expander("Course Objectives"):
                st.write('\n'.join(result['course_objectives']))
            study_materials = ""
            for i in result['study_materials']:
                study_materials = study_materials + f"**{i['material']}**"
                study_materials += "\n  ->"
                study_materials += i['purpose']
                study_materials += "\n\n"
            with st.expander("Study Materials"):
                st.write(study_materials)

            course_outline = ""
            for i in result['course_outline']:
                course_outline = course_outline + f"**{i['duration']}** - **{i['topic']}**"
                course_outline += "\n\n"
                course_outline += f"-> {i['subtopics'][0]}"
                course_outline += "\n\n"
            with st.expander("Course Outline"):
                st.write(course_outline)
            grading_policy = ""
            for i in result['grading_policy']:
                grading_policy += f"**{i['Component']}** ({i['Coefficient']})"
                grading_policy += "\n\n"
                grading_policy += f"-> {i['Note']}"
                grading_policy += "\n\n"
            with st.expander("Grading Policy"):
                st.write(grading_policy)
            rules = ""
            for i in result['rules_policies']:
                rules += f"**{i}**"
                for rule in result['rules_policies'][i]:
                    rules += f"\n\n->{rule}"
                rules += "\n\n"
            with st.expander("Rules"):
                st.write(rules)
            st.json(result)
            #st.json(result)

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
            # elif output_type == 'word':
            #     word_gen = WordGenerator(grade, subject)
            #     word_file = word_gen.generate_word(result)
            #     st.success("Word document generated successfully!")
            #     st.download_button(
            #         label="Download Word Document",
            #         data=word_file,
            #         file_name=f"{grade}_{subject}_syllabus.docx",
            #         mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            #     )
            # else:
            #     st.json(result)

        except Exception as e:
            error_message = f"Error in execution: {e}"
            st.error(error_message)
