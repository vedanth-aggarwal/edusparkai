import streamlit as st
#from audio_converter.transcribe import Audio
#from audio_converter.summary import LLM
#from audio_converter.mp4_converter import VideoConverter
#from audio_converter.yt_converter import youtube_converter
from flashcard_generator.tools2 import youtube_converter,YoutubeProcessor, Processor

from pydantic import BaseModel, HttpUrl, Field
from typing import Dict
from langchain_core.output_parsers import JsonOutputParser

class ConceptDefinition(BaseModel):
    concepts: Dict[str, str] = Field(description="A dictionary of key concepts and their definitions")
    #concept: str = Field(description="A key concept found in the text")
    #definition: str = Field(description="Definition of the key concept")
# Set up the parser with the Pydantic model
parser = JsonOutputParser(pydantic_object=ConceptDefinition)


import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/env3/bin/ffmpeg"

def main():
    st.title("Flashcard Generator")

    transcript = None  # Initialize transcript variable

    st.header("Enter the YouTube URL")
    youtube_url = st.text_input("YouTube URL", "")
    if youtube_url:
            # Extract the video ID from the YouTube URL
            with st.spinner("Extracting video ID..."):
                yt_converter = youtube_converter(youtube_url)
                st.success(youtube_url)
                transcript = yt_converter.display_transcript()
            

    # Display the transcript and summary if available
    if transcript:
        with st.expander("📜 Full Transcript"):
            st.text_area("Transcript", transcript, height=300)
        
        processor = Processor('llama-3.1-70b-versatile')
        yt_processor = YoutubeProcessor(processor,parser)
        #option = st.radio("Choose your task:", ("Generate Summary", "Generate Quiz"))    

        result = yt_processor.retrieve_youtube_documents(transcript, verbose=False)
    
        #summary = genai_processor.generate_document_summary(result, verbose=True)
        
        # Find key concepts
        raw_concepts = yt_processor.find_key_concepts(result, verbose=True)
        
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
        return {
            "key_concepts": key_concepts_list
        }

if __name__ == "__main__":
    main()
