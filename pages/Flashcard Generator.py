# Streamlit-based UI Code
import streamlit as st
import os
import base64
from rubric_generator.tools import RUBRIC
from pydantic import BaseModel, HttpUrl, Field
from typing import Dict
from langchain_core.output_parsers import JsonOutputParser

# Function to save uploaded file temporarily
def save_uploaded_file(uploaded_file):
    """Saves an uploaded file to a temporary location."""
    temp_path = os.path.join("temp_uploads", uploaded_file.name)
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

# Streamlit app setup
st.title("FLASHCARD Generator Tool")

# Form for user input
with st.form("flashcard_form"):
    #file = st.file_uploader("Upload a file (optional)", type=["pdf", "docx", "txt"])
    youtube_url = st.text_input("YouTube URL", "")

    # Form submit button
    submitted = st.form_submit_button("Generate RUBRIC")

if submitted:
    try:
        # Check if required inputs are provided
        if not youtube_url:
            st.error("All input fields (grade, points, standard, and assignment) are required.")
        else:
            os.makedirs("temp_uploads", exist_ok=True)
            #saved_file_path = save_uploaded_file(file)

            os.environ['GRPC_DNS_RESOLVER'] = 'native'

            class ConceptDefinition(BaseModel):
                concepts: Dict[str, str] = Field(description="A dictionary of key concepts and their definitions")
                #concept: str = Field(description="A key concept found in the text")
                #definition: str = Field(description="Definition of the key concept")
            # Set up the parser with the Pydantic model
            parser = JsonOutputParser(pydantic_object=ConceptDefinition)

            from flashcard_generator.services.genai import (
                YoutubeProcessor,
                GeminiProcessor
            )

            class VideoAnalysisRequest(BaseModel):
                youtube_link: HttpUrl
                # advanced settings

            genai_processor = GeminiProcessor(
                    model_name = "llama-3.1-70b-versatile",
                    project = "" #"gemini-dynamo-428115" #ai-dev-cqc-q1-2024 #gemini-quizzify-427910
                )

            def analyze_video(request: VideoAnalysisRequest):
                # Doing the analysis
                processor = YoutubeProcessor(genai_processor = genai_processor,parser=parser)
                result = processor.retrieve_youtube_documents(youtube_url, verbose=False)
                
                #summary = genai_processor.generate_document_summary(result, verbose=True)
                
                # Find key concepts
                raw_concepts = processor.find_key_concepts(result, verbose=True)
                
                # Deconstruct
                #unique_concepts = {}
                #for concept_dict in raw_concepts:
                #    print(concept_dict)
                #    for key, value in concept_dict.items():
                #        unique_concepts[key] = value
                
                # Reconstruct
                #key_concepts_list = [{key: value} for key, value in concept_dict.items()]
                key_concepts_list = []
                for content in raw_concepts:
                    key_concepts_list.extend([{'term':key,'definition':value} for key, value in content['concepts'].items()])
                #key_concepts_list = [{key: value} for key, value in raw_concepts[i]['concepts'].items() for i in range(len(raw_concepts))]
                st.json({
                    "key_concepts": key_concepts_list
                })








            # Initialize the RUBRIC generator and run it
            #gen = RUBRIC(grade, points, standard, saved_file_path)
            #result = gen.run()

            # pdf_file = "dynamic_rubric.pdf"

            #             # Display result and generated PDF
            # pdf_file = "dynamic_rubric.pdf"
            # with open(pdf_file, "rb") as pdf:
            #     st.success("RUBRIC generated successfully!")
            #     pdf_data = pdf.read()
                
            #     ## Option 1: Embed PDF for display
            #     base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
            #     #pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="900" frameborder="0"></iframe>'
            #     #st.markdown(pdf_display, unsafe_allow_html=True)

            #     # Option 2: Direct link to download the PDF
            #     st.download_button(
            #         label="Download PDF",
            #         data=pdf_data,
            #         file_name=pdf_file,
            #         mime="application/pdf"
            #     )

            #     # Option 3: Link to view PDF in new tab
            #     st.markdown(f"[View PDF](data:application/pdf;base64,{base64_pdf})", unsafe_allow_html=True)
            
            

    except Exception as e:
        error_message = f"Error in execution: {e}"
        st.error(error_message)
