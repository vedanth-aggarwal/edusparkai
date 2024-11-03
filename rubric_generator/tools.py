import os
import json
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path

model_name = 'llama-3.1-70b-versatile'

class RUBRIC:
    def __init__(self, grade, points, standard, assignment_path, path=""):
        self.grade = grade
        self.points = points
        self.standard = standard
        self.assignment_path = assignment_path  # Assignment path is passed here
        self.path = path
        self.model = ChatGroq(model=model_name, temperature=0.3, api_key="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")

    def read_text_file(self, filepath):
        """Reads text from a file."""
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()

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

    def genpdf(self, rubric_data):
        """Generates a PDF document from rubric data."""
        pdf_file = "dynamic_rubric.pdf"
        pdf = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        
        table_data = []
        iteration = 1
        for item in rubric_data:
            for criteria, category in item.items():
                categories = list(category)
                if iteration == 1:
                    table_data.append([
                        Paragraph(f"<b>Criteria</b>", styles['Normal']),
                        Paragraph(f"<b>{categories[0]}</b>", styles['Normal']),
                        Paragraph(f"<b>{categories[1]}</b>", styles['Normal']),
                        Paragraph(f"<b>{categories[2]}</b>", styles['Normal']),
                        Paragraph(f"<b>{categories[3]}</b>", styles['Normal'])
                    ])
                    iteration += 1
                table_data.append([
                    Paragraph(f"<b>{criteria}</b>", styles['Normal']),
                    Paragraph(category.get(categories[0], ''), styles['Normal']),
                    Paragraph(category.get(categories[1], ''), styles['Normal']),
                    Paragraph(category.get(categories[2], ''), styles['Normal']),
                    Paragraph(category.get(categories[3], ''), styles['Normal'])
                ])

        table = Table(table_data, colWidths=[150, 100, 100, 100, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements = [table]
        pdf.build(elements)
        print(f"PDF created successfully at {pdf_file}")

    def run(self):
        """Main execution function to generate the rubric."""
        assignment_content = self.extract_content_from_file(self.assignment_path)  # Use file path directly
        print(assignment_content)
        
        # Here you can implement your prompt building and model invocation logic...
        # response = chain.invoke(...)
        
        # Placeholder for response handling, adjust this according to your logic
        response = {}  # Replace with actual response from model invocation
        self.genpdf(response)
        return response
