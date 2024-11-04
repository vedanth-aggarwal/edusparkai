import os
import json
import time
import requests
import pandas as pd
from langchain_core.prompts import PromptTemplate
# from langchain_google_vertexai import VertexAI
import re
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib import colors
from docx import Document
from requests.exceptions import HTTPError
from io import BytesIO
# from bs4 import BeautifulSoup
import requests
# import praw
# import prawcore
from langchain_groq import ChatGroq
import requests
import os
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
#from app.features.syllabus_generator import credentials
from pathlib import Path
model_name = 'llama-3.1-70b-versatile'
# Entire syllabus generator pipeline with all functions in this class
class AIRAG :

    def __init__(self,grade,assignment,description='',path=""):
        self.grade = grade
        self.assignment = assignment
        self.description = description
        self.path = path
        self.model = ChatGroq(model=model_name,temperature=0.3,api_key="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")

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
        else:
            raise Exception(f"Unsupported file type: {content_type}. Unable to extract content.")

    def run(self):
        # Important study resources and their specific function
        current_dir = Path(__file__).parent

        prompt = self.build_prompt(current_dir / 'prompt.txt')
        chain = prompt | self.model
        assignment_content = self.extract_content_from_file(self.assignment)
        #print(assignment_content)
        
        original_response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'assignment' : assignment_content,
                            'description':self.description
                        })
        original_response = self.validator(original_response.content)
        #response = self.validator(response.content)

        prompt = self.build_prompt(current_dir / 'prompt1.txt')
        chain = prompt | self.model
        critique = chain.invoke(
                        {
                            'grade' : self.grade,
                            'assignment' : assignment_content,
                            'description':self.description,
                            'input':original_response
                        }).content
        
        print(critique)
        prompt = self.build_prompt(current_dir / 'prompt2.txt')
        chain = prompt | self.model
        final_response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'assignment' : assignment_content,
                            'description':self.description,
                            'input':original_response,
                            'critique':critique
                        }).content
        #print(response.content)
        response = self.validator(final_response)
        print(response)
        return response 

"""
{{
        "assignment description":"step by step procedure",
        "explanation":"reasoning behind assignment and how modifications make it AI resistant"
    }},
    {{
        "assignment description":"step by step procedure",
        "explanation":"reasoning behind assignment and how modifications make it AI resistant"
    }},
    {{
        "assignment description":"step by step procedure",
        "explanation":"reasoning behind assignment and how modifications make it AI resistant"
    }}

"""
# Search engine class to extract api output and verify data
'''
class Search_engine:

    def __init__(self, grade, subject, API_KEY=credentials['api_key'],SEARCH_ENGINE_ID=credentials['search_engine_id']):
        self.grade = grade
        self.subject = subject
        self.API_KEY = API_KEY
        self.SEARCH_ENGINE_ID = SEARCH_ENGINE_ID

    def get_link(self):
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'q': f'syllabus of {self.subject} {self.grade} level',
            'key': self.API_KEY,
            'cx': self.SEARCH_ENGINE_ID
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            links = [item['link'] for item in data.get('items', [])]
            if not links:
                print("No links found in the search results.")
            return links[0]
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Log the error
            return ''
        except Exception as err:
            print(f"Other error occurred: {err}")  # Log the error
            return ''
        return ''

    def scrap_data(self):
        link = self.get_link()
        if not link :
            return []
        try:
            return pd.read_html(link)
        except ValueError as e:
            print(f"Error scraping data: {e}")  # Handle and log the scraping error
            return []
'''
