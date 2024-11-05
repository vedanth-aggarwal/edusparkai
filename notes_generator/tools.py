#imports
from langchain_core.prompts import PromptTemplate
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
import json
from langchain_groq import ChatGroq

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Frame, PageTemplate, BaseDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from youtube_transcript_api import YouTubeTranscriptApi
from moviepy.editor import VideoFileClip
import tempfile
import io
import assemblyai as aai
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json
from pathlib import Path

model_name = 'llama-3.1-70b-versatile'

class NotesGenerator:

    def __init__(self,model, notes_content, path="", orientation="portrait",columns=1):
        self.model = ChatGroq(model = model_name, temperature=0.3, api_key="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")
        self.notes_content = notes_content
        self.path = path
        self.orientation = orientation
        self.columns = columns

    def read_text_file(self, filepath):
        """Reads text from a file."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    
    def build_prompt(self,filepath):
        # build invididual promps for each sub part of syllabus
        template = self.read_text_file(filepath)

        prompt = PromptTemplate.from_template(template)
        return prompt

    def extract_text_from_txt(self, file_path):
        """Extracts text from a TXT file."""
        return self.read_text_file(file_path)

    def extract_text_from_pdf(self, file_path):
        """Extracts text from a PDF file."""
        text = ''
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() or ''
        return text

    def extract_text_from_docx(self, file_path):
        """Extracts text from a DOCX file."""
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    
    def validator(self,response):
        data = []
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print("JSON Decode Error , Trying to correct the JSON")
            try:
                corrected_result = response[min(response.find('{'),response.find('[')):max(response.rfind(']'),response.rfind('}')) + 1]
                data = json.loads(corrected_result)
                print("Corrected Parsed JSON successfully")
            except json.JSONDecodeError as e:
                print("Failed to parse corrected JSON")
        return data

    
    def extract_content_from_file(self, file_path):
        """Determines file type and extracts content accordingly."""
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        elif file_path.endswith('.txt'):
            return self.extract_text_from_txt(file_path)
        else:
            raise Exception("Unsupported file type. Only .pdf, .docx, and .txt are supported.")

    def extract_content_from_url(self,file_url):
        file_content, content_type = self.download_file(file_url)

        # Check the Content-Type header for file type
        if 'application/pdf' in content_type:
            print("Extracting content from PDF...")
            return self.extract_text_from_pdf(file_content)
        elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
            print("Extracting content from Word Document (.docx)...")
            return self.extract_text_from_docx(file_content)
        elif 'text/plain' in content_type or 'text/html' in content_type:
            print("Extracting content from Text File...")
            return self.extract_text_from_txt(file_content)
        elif 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
            print("Extracting content from MP3...")
            return self.extract_text_from_mp3(file_content)
        elif 'video/mp4' in content_type:
            print("Extracting content from MP4...")
            return self.extract_text_from_mp4(file_content)
        elif 'youtube.com' in file_url or 'youtu.be' in file_url:
            print("Extracting content from YouTube URL...")
            return self.extract_text_from_youtube(file_url)
        elif 'application/vnd.openxmlformats-officedocument.presentationml.presentation' in content_type:
            print("Extracting content from PowerPoint (.pptx)...")
            return self.extract_text_from_pptx(file_content)
        else:
            raise Exception(f"Unsupported file type: {content_type}. Unable to extract content.")


    def run(self):

        current_dir = Path(__file__).parent
        prompt = self.build_prompt(current_dir / 'prompt.txt')

        chain = prompt | self.model

        notes_content = self.extract_content_from_file(self.notes_content)
        print(notes_content)

        response = chain.invoke(
            {
                "notes_content": notes_content
        })

        response = response.content

        #response = self.validator(response.content)

        #self.generate_notes_pdf(response)
        print(response)
        return response

    



