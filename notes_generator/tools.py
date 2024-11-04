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
        self.notes_conent = notes_content
        self.path = path
        self.orientation = orientation
        self.columns = columns

    def read_text_file(self,filepath):

        with open(f"{self.path}{filepath}", 'r') as file:
            return file.read()
        
    def build_prompt(self,filepath):
        # build invididual promps for each sub part of syllabus
        template = self.read_text_file(filepath)

        prompt = PromptTemplate.from_template(template)
        return prompt
    
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

    def extract_text_from_txt(self,file_content):
        return file_content.decode('utf-8')

    def extract_text_from_pdf(self,file_content):
        pdf_reader = PdfReader(BytesIO(file_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def extract_text_from_docx(self,file_content):
        doc = Document(BytesIO(file_content))
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text

    def extract_text_from_youtube(self, video_url):
            video_id = self.extract_video_id(video_url)
            if video_id:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    return "".join([entry['text'] for entry in transcript])
                except Exception as e:
                    print(f"Error retrieving YouTube transcript: {e}")
                    return "No transcript available."
            else:
                print("Invalid YouTube URL.")
                return "No transcript available."

    def extract_video_id(self, url):
        if "youtu.be/" in url:
            return url.split('/')[-1]
        elif "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        return None

    def extract_text_from_mp4(self, video_file):
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            temp_file.write(video_file.read())
            temp_file.seek(0)

            video = VideoFileClip(temp_file.name)
            temp_mp3_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            video.audio.write_audiofile(temp_mp3_file.name)

            with open(temp_mp3_file.name, "rb") as f:
                mp3_buffer = io.BytesIO(f.read())

            mp3_buffer.seek(0)
            temp_file.close()
            temp_mp3_file.close()

            return self.extract_text_from_mp3(mp3_buffer)

        except Exception as e:
            print(f"Error extracting text from MP4: {e}")
            return "Failed to extract content from MP4."

    def extract_text_from_mp3(self, audio_file):
        aai.settings.api_key = "b82693154c7a4a7ca95675dd807a3fe7"
        config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code="en_us")
        transcriber = aai.Transcriber(config=config)

        try:
            transcript = transcriber.transcribe(audio_file)
            if transcript.status == aai.TranscriptStatus.error:
                print(f"Transcription error: {transcript.error}")
                return "Failed to transcribe audio."
            else:
                return transcript.text

        except Exception as e:
            print(f"Error in MP3 transcription: {e}")
            return "Failed to transcribe audio."
    
    def extract_text_from_pptx(self, file_content):
        """
        Extracts text from a PPTX file.
        """
        text = ""
        try:
            ppt = "" # Presentation(BytesIO(file_content))
            for slide in ppt.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text += shape.text + "\n"
        except Exception as e:
            print(f"Error extracting text from PPTX: {e}")
            text = "Failed to extract content from PPTX."

        return text


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
        
    
    def generate_notes_pdf(self, response):
        output_filename = "generated_notes.pdf"
        page_size = landscape(letter) if self.orientation == 'landscape' else letter
        styles = getSampleStyleSheet()

        # Create PDF template
        if self.columns == 2:
            # Define two-column layout
            frame1 = Frame(inch, inch, (page_size[0] / 2) - 2 * inch, page_size[1] - 2 * inch, id='col1')
            frame2 = Frame((page_size[0] / 2) + inch, inch, (page_size[0] / 2) - 2 * inch, page_size[1] - 2 * inch, id='col2')
            template = PageTemplate(frames=[frame1, frame2])
        else:
            # Define single-column layout
            frame = Frame(inch, inch, page_size[0] - 2 * inch, page_size[1] - 2 * inch, id='single_col')
            template = PageTemplate(frames=[frame])

        # Set up the PDF document
        doc = BaseDocTemplate(output_filename, pagesize=page_size)
        doc.addPageTemplates([template])

        # Build the content
        content = []

        # Add summary
        summary_text = response.get('summary', 'No summary available.')
        content.append(Paragraph(f"<b>Summary:</b><br />{summary_text}", styles['Normal']))
        content.append(Spacer(1, 12))

        # Add outline
        outline = response.get('outline', [])
        for item in outline:
            content.append(Paragraph(item, styles['Bullet']))
            content.append(Spacer(1, 8))

        # Build the PDF
        doc.build(content)
        print(f"Notes generated and saved as {output_filename}")


    def run(self):

        current_dir = Path(__file__).parent
        prompt = self.build_prompt(current_dir / 'prompt.txt')

        chain = prompt | self.model

        notes_content = self.extract_content_from_url(self.notes_conent)
        print(notes_content)

        response = chain.invoke(
            {
                "notes_content": notes_content
        })

        print(response.content)

        response = self.validator(response.content)

        self.generate_notes_pdf(response)
        print(response)
        return response

    



