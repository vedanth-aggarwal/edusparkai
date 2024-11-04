import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException
from langchain import hub
from langchain.agents import AgentExecutor,create_react_agent,tool
from langchain_community.document_loaders import WebBaseLoader
from langchain.chains.summarize.chain import load_summarize_chain
from langchain.tools.base import StructuredTool
from langchain_groq import ChatGroq
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import PromptTemplate
import json


from bs4 import BeautifulSoup

model_name = 'llama-3.1-70b-versatile'

class CONNECT:

    def __init__(self,grade,subject,description='',path=""):
        self.grade = grade
        self.subject = subject
        self.description = description
        self.path = path
        self.model = ChatGroq(model=model_name,temperature=0.3,api_key="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")
        self.prompt = """
    You are an AI that helps teachers make learning more engaging and relevant to their students , based on some informations from the teacher,
    generate 3 creative techniques to incorporate personalized aspects ... into teaching the subject.
    For each technique, provide a Recommendation Rationale that explains why it was suggested,
    highlighting how the recommendation connects to the teaching content and enhances student engagement, considering the students' interests or background.

    Return the result so it can be loaded using json.loads in python , a List of objects following this schema:

    [
        {{
            'project title':'...',
            'recommendation':'...',
            'Rationale':'...'
        }},
        ...,
        {{
            'More informations':'this is an optional paragraph where you can add a further comment or informations,sources ...'
        }}
    ]
    Teacher informations : I teach {subject} to {grade} students
    Description: {description}
 """

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

    def run(self):

        prompt = self.build_prompt(self.prompt)
        chain = prompt | self.model
        #assignment_content = self.extract_content_from_file(self.assignment)
        #print(assignment_content)
        
        original_response = chain.invoke(
                        {
                            'grade' : self.grade,
                            'subject' : self.subject,
                            'description':self.description
                        })
        
        response = self.validator(original_response.content)
        return response 
    
