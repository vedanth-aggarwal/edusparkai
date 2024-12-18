# pdf_processing.py

# Necessary imports
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
import uuid
import faiss
import numpy as np
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter

#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\\Users\\vedan\\OneDrive\Documents\\gemini_quizzify\\mission-quizify\\authentication.json'

class DocumentProcessor:
    """
    This class encapsulates the functionality for processing uploaded PDF documents using Streamlit
    and Langchain's PyPDFLoader. It provides a method to render a file uploader widget, process the
    uploaded PDF files, extract their pages, and display the total number of pages extracted.
    """
    def __init__(self):
        self.pages = []  # List to keep track of pages from all documents
    
    def ingest_documents(self):
        """
        Renders a file uploader in a Streamlit app, processes uploaded PDF files,
        extracts their pages, and updates the self.pages list with the total number of pages.
        
        Given:
        - Handling of temporary files with unique names to avoid conflicts.
        
        Your Steps:
        1. Utilize the Streamlit file uploader widget to allow users to upload PDF files.
           Hint: Look into st.file_uploader() with the 'type' parameter set to 'pdf'.
        2. For each uploaded PDF file:
           a. Generate a unique identifier and append it to the original file name before saving it temporarily.
              This avoids name conflicts and maintains traceability of the file.
           b. Use Langchain's PyPDFLoader on the path of the temporary file to extract pages.
           c. Clean up by deleting the temporary file after processing.
        3. Keep track of the total number of pages extracted from all uploaded documents.
        
        Example for generating a unique file name with the original name preserved:
        ```
        unique_id = uuid.uuid4().hex
        temp_file_name = f"{original_name}_{unique_id}{file_extension}"
        ```
        """
        
        # Step 1: Render a file uploader widget. Replace 'None' with the Streamlit file uploader code.
        uploaded_files = st.file_uploader('Upload Files',type='pdf',accept_multiple_files=True)
            #####################################
            # Allow only type `pdf`
            # Allow multiple PDFs for ingestion
            #####################################
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # Generate a unique identifier to append to the file's original name
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                # Write the uploaded PDF to a temporary file
                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())

                loader = PyPDFLoader(temp_file_path)
                documents = loader.load()
                #extracted_pages = document.pages

                # Step 3: Add the extracted pages to the 'pages' list
                self.pages.extend(documents)
                print(len(self.pages))
                # Step 2: Process the temporary file
                #####################################
                # Use PyPDFLoader here to load the PDF and extract pages.
                # https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf#using-pypdf
                # You will need to figure out how to use PyPDFLoader to process the temporary file.
                
                # Step 3: Then, Add the extracted pages to the 'pages' list.
                #####################################
                
                # Clean up by deleting the temporary file.
                os.unlink(temp_file_path)
            
            # Display the total number of pages processed.
            st.write(f"Total pages processed: {len(self.pages)}")
        
#if __name__ == "__main__":
#    processor = DocumentProcessor()
#    processor.ingest_documents()

# embedding_client.py
import streamlit as st
#from langchain_google_vertexai import VertexAIEmbeddings
import os
from sentence_transformers import SentenceTransformer
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\\Users\\vedan\\OneDrive\Documents\\gemini_quizzify\\mission-quizify\\authentication.json'
class EmbeddingClient:
    """
    Task: Initialize the EmbeddingClient class to connect to Google Cloud's VertexAI for text embeddings.

    The EmbeddingClient class should be capable of initializing an embedding client with specific configurations
    for model name, project, and location. Your task is to implement the __init__ method based on the provided
    parameters. This setup will allow the class to utilize Google Cloud's VertexAIEmbeddings for processing text queries.

    Steps:
    1. Implement the __init__ method to accept 'model_name', 'project', and 'location' parameters.
       These parameters are crucial for setting up the connection to the VertexAIEmbeddings service.

    2. Within the __init__ method, initialize the 'self.client' attribute as an instance of VertexAIEmbeddings
       using the provided parameters. This attribute will be used to embed queries.

    Parameters:
    - model_name: A string representing the name of the model to use for embeddings.
    - project: The Google Cloud project ID where the embedding model is hosted.
    - location: The location of the Google Cloud project, such as 'us-central1'.

    Instructions:
    - Carefully initialize the 'self.client' with VertexAIEmbeddings in the __init__ method using the parameters.
    - Pay attention to how each parameter is used to configure the embedding client.

    Note: The 'embed_query' method has been provided for you. Focus on correctly initializing the class.
    """
    
    def __init__(self, model_name):
        self.model_name = model_name
        #self.project = project
        #self.location = location

        # Initialize the VertexAIEmbeddings client with the given parameters
        # Read about the VertexAIEmbeddings wrapper from Langchain here
        # https://python.langchain.com/docs/integrations/text_embedding/google_generative_ai
        self.client = SentenceTransformer(
            self.model_name
        )
        
    def embed_query(self, query):
        """
        Uses the embedding client to retrieve embeddings for the given query.

        :param query: The text query to embed.
        :return: The embeddings for the query or None if the operation fails.
        """
        vectors = self.client.encode(query)
        return vectors
    
    def embed_documents(self, documents):
        """
        Retrieve embeddings for multiple documents.

        :param documents: A list of text documents to embed.
        :return: A list of embeddings for the given documents.
        """
        try:
            return self.client.encode(documents)
        except AttributeError:
            print("Method embed_documents not defined for the client.")
            return None

import sys
import os
import streamlit as st
# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embeddings_config: An embedding client for embedding documents.
        """
        self.processor = processor      # This will hold the DocumentProcessor from Task 3
        self.embed_model = embed_model  # This will hold the EmbeddingClient from Task 4
        self.db = None                  # This will hold the Chroma collection
    
    def create_chroma_collection(self):

        """
        Task: Create a Chroma collection from the documents processed by the DocumentProcessor instance.
        
        Steps:
        1. Check if any documents have been processed by the DocumentProcessor instance. If not, display an error message using streamlit's error widget.
        
        2. Split the processed documents into text chunks suitable for embedding and indexing. Use the CharacterTextSplitter from Langchain to achieve this. You'll need to define a separator, chunk size, and chunk overlap.
        https://python.langchain.com/docs/modules/data_connection/document_transformers/
        
        3. Create a Chroma collection in memory with the text chunks obtained from step 2 and the embeddings model initialized in the class. Use the Chroma.from_documents method for this purpose.
        https://python.langchain.com/docs/integrations/vectorstores/chroma#use-openai-embeddings
        https://docs.trychroma.com/getting-started
        
        Instructions:
        - Begin by verifying that there are processed pages available. If not, inform the user that no documents are found.
        
        - If documents are available, proceed to split these documents into smaller text chunks. This operation prepares the documents for embedding and indexing. Look into using the CharacterTextSplitter with appropriate parameters (e.g., separator, chunk_size, chunk_overlap).
        
        - Next, with the prepared texts, create a new Chroma collection. This step involves using the embeddings model (self.embed_model) along with the texts to initialize the collection.
        
        - Finally, provide feedback to the user regarding the success or failure of the Chroma collection creation.
        
        Note: Ensure to replace placeholders like [Your code here] with actual implementation code as per the instructions above.
        """
        
        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Step 2: Split documents into text chunks
        # Use a TextSplitter from Langchain to split the documents into smaller text chunks
        # https://python.langchain.com/docs/modules/data_connection/document_transformers/character_text_splitter
        splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=100)
        texts = splitter.split_documents(self.processor.pages)
        
        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        # Step 3: Create the Chroma Collection
        # https://docs.trychroma.com/
        # Create a Chroma in-memory client using the text chunks and the embeddings model
        self.db = Chroma.from_documents(texts, self.embed_model)
        
        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")
    
    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        :param query: The query string to search for in the Chroma collection.
        
        Returns the first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")


import sys
import os
import streamlit as st
from langchain_groq import ChatGroq
import streamlit as st
from langchain_core.prompts import PromptTemplate
import os
import sys 

# https://www.youtube.com/watch?v=NQWfvhw7OcI&t=678s
# https://blog.futuresmart.ai/unlocking-the-potential-of-langchain-expression-language-lcel-a-hands-on-guide?showSharer=true

import streamlit as st
import os
import sys
import json
#sys.path.append(os.path.abspath('../../'))
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

class Choice(BaseModel):
    key: str = Field(description="The key for the choice, should be one of 'A', 'B', 'C', or 'D'.")
    value: str = Field(description="The text of the choice.")

class QuestionSchema(BaseModel):
    question: str = Field(description="The text of the question.")
    choices: List[Choice] = Field(description="A list of choices for the question, each with a key and a value.")
    answer: str = Field(description="The key of the correct answer from the choices list.")
    explanation: str = Field(description="An explanation as to why the answer is correct.")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What is the capital of France?",
                "choices": [
                    {"key": "A", "value": "Berlin"},
                    {"key": "B", "value": "Madrid"},
                    {"key": "C", "value": "Paris"},
                    {"key": "D", "value": "Rome"}
                ],
                "answer": "C",
                "explanation": "Paris is the capital of France."
              }
          """
        }
      }

import faiss
import numpy as np
import streamlit as st
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

class FAISSCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializes the FAISSCollectionCreator with a DocumentProcessor instance and an embeddings model.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embed_model: An embedding client for embedding documents.
        """
        self.processor = processor
        self.embed_model = embed_model
        self.vectorstore = None  # LangChain's FAISS vector store
        self.document_store = {}  # To store document metadata
        self.retriever = None

    def create_chroma_collection(self):
        """
        Creates a FAISS index from the documents processed by the DocumentProcessor instance using LangChain.
        """
        # Step 1: Check for processed documents
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Step 2: Split documents into text chunks
        splitter = CharacterTextSplitter(separator='\n', chunk_size=1000, chunk_overlap=100)
        texts = splitter.split_documents(self.processor.pages)

        if texts:
            st.success(f"Successfully split pages into {len(texts)} documents!", icon="✅")

        # Step 3: Use LangChain FAISS to create index
        self.vectorstore = FAISS.from_texts(
            [text.page_content for text in texts], 
            self.embed_model
        )
        
        self.retriever = self.vectorstore.as_retriever()

        # Store document metadata
        for i, text in enumerate(texts):
            self.document_store[i] = text.page_content

        if self.vectorstore is not None:
            st.success("Successfully created FAISS Index using LangChain!", icon="✅")
        else:
            st.error("Failed to create FAISS Index!", icon="🚨")

    def query_chroma_collection(self, query) -> str:
        """
        Queries the created FAISS index for documents similar to the query.
        :param query: The query string to search for in the FAISS index.
        
        Returns the most similar document from the index.
        """
        if self.vectorstore:
            query_results = self.retriever.get_relevant_documents(query)

            if query_results:
                similar_doc = query_results[0].page_content
                st.success("Found a matching document!", icon="✅")
                return similar_doc
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("FAISS Index has not been created!", icon="🚨")

class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions for the quiz,
        and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum of 10.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information related to the quiz topic.
        """
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        self.num_questions = num_questions

        self.vectorstore = vectorstore
        #self.embeddings = embeddings
        self.llm = None
        self.parser = JsonOutputParser(pydantic_object=QuestionSchema)
        self.question_bank = [] # Initialize the question bank to store questions
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            {format_instructions}
            
            Context: {context}
            """
    
    def init_llm(self):
        """
        Initializes and configures the Large Language Model (LLM) for generating quiz questions.

        This method should handle any setup required to interact with the LLM, including authentication,
        setting up any necessary parameters, or selecting a specific model.

        :return: An instance or configuration for the LLM.
        """
        model_name = 'llama-3.1-70b-versatile'
        self.llm = ChatGroq(model=model_name,temperature=0.3,api_key="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")



    def generate_question_with_vectorstore(self):
        """
        Generates a quiz question based on the topic provided using a vectorstore

        :return: A JSON object representing the generated quiz question.
        """
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")
        

        # Enable a Retriever
        retriever = self.vectorstore #.as_retriever()
        
        # Use the system template to create a PromptTemplate
        prompt = PromptTemplate(
            template = self.system_template,
            input_variables=["topic", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        
        st.success('GEN QUIZ CHECKPOINT')
        # RunnableParallel allows Retriever to get relevant documents
        # RunnablePassthrough allows chain.invoke to send self.topic to LLM
        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        # Create a chain with the Retriever, PromptTemplate, and LLM
        chain = setup_and_retrieval | prompt | self.llm | self.parser

        # Invoke the chain with the topic as input
        response = chain.invoke(self.topic)
        return response

    def generate_quiz(self) -> list:
        """
        Task: Generate a list of unique quiz questions based on the specified topic and number of questions.

        This method orchestrates the quiz generation process by utilizing the `generate_question_with_vectorstore` method to generate each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.

        Steps:
            1. Initialize an empty list to store the unique quiz questions.
            2. Loop through the desired number of questions (`num_questions`), generating each question via `generate_question_with_vectorstore`.
            3. For each generated question, validate its uniqueness using `validate_question`.
            4. If the question is unique, add it to the quiz; if not, attempt to generate a new question (consider implementing a retry limit).
            5. Return the compiled list of unique quiz questions.

        Returns:
        - A list of dictionaries, where each dictionary represents a unique quiz question generated based on the topic.

        Note: This method relies on `generate_question_with_vectorstore` for question generation and `validate_question` for ensuring question uniqueness. Ensure `question_bank` is properly initialized and managed.
        """
        self.question_bank = [] # Reset the question bank

        for _ in range(self.num_questions):
            # ##### YOUR CODE HERE #####
            question = self.generate_question_with_vectorstore()
            # # Validate the question using the validate_question method
            if self.validate_question(question):
                print("Successfully generated unique question")
                # Add the valid and unique question to the bank
                self.question_bank.append(question)
            else:
                print("Duplicate or invalid question detected.")
            ##### YOUR CODE HERE #####
                for i in range(3): #Retry limit of 3 attempts
                    question_str = self.generate_question_with_vectorstore()
                    
                    try:
                        question = json.loads(question_str)
                    except json.JSONDecodeError:
                        print("Failed to decode question JSON.")
                        continue 
                    
                    if self.validate_question(question):
                        print("Successfully generated unique question")
                        self.question_bank.append(question)
                        break
                    else:
                        print("Duplicate or invalid question detected - Attempt "+(i+1))
                        continue

        return self.question_bank

    def validate_question(self, question: dict) -> bool:
        """
        Task: Validate a quiz question for uniqueness within the generated quiz.

        This method checks if the provided question (as a dictionary) is unique based on its text content compared to previously generated questions stored in `question_bank`. The goal is to ensure that no duplicate questions are added to the quiz.

        Steps:
            1. Extract the question text from the provided dictionary.
            2. Iterate over the existing questions in `question_bank` and compare their texts to the current question's text.
            3. If a duplicate is found, return False to indicate the question is not unique.
            4. If no duplicates are found, return True, indicating the question is unique and can be added to the quiz.

        Parameters:
        - question: A dictionary representing the generated quiz question, expected to contain at least a "question" key.

        Returns:
        - A boolean value: True if the question is unique, False otherwise.

        Note: This method assumes `question` is a valid dictionary and `question_bank` has been properly initialized.
        """
        ##### YOUR CODE HERE #####
        # Consider missing 'question' key as invalid in the dict object


        if 'question' not in question or not question['question']:
            raise ValueError("The dict object must contain a non-empty 'question' key")

        # Check if a question with the same text already exists in the self.question_bank

        is_unique = True

        for question_iterated in self.question_bank:
            if(question_iterated['question'] == question['question']):
                is_unique = False
                break

        ##### YOUR CODE HERE #####
        return is_unique



import streamlit as st
import os
import sys
import json

class QuizManager:
    ##########################################################
    def __init__(self, questions: list):
        """
        Task: Initialize the QuizManager class with a list of quiz questions.

        Overview:
        This task involves setting up the `QuizManager` class by initializing it with a list of quiz question objects. Each quiz question object is a dictionary that includes the question text, multiple choice options, the correct answer, and an explanation. The initialization process should prepare the class for managing these quiz questions, including tracking the total number of questions.

        Instructions:
        1. Store the provided list of quiz question objects in an instance variable named `questions`.
        2. Calculate and store the total number of questions in the list in an instance variable named `total_questions`.

        Parameters:
        - questions: A list of dictionaries, where each dictionary represents a quiz question along with its choices, correct answer, and an explanation.

        Note: This initialization method is crucial for setting the foundation of the `QuizManager` class, enabling it to manage the quiz questions effectively. The class will rely on this setup to perform operations such as retrieving specific questions by index and navigating through the quiz.
        """
        ##### YOUR CODE HERE #####
        self.questions = questions
        self.total_questions = len(self.questions)
    ##########################################################

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds,
        it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        # Ensure index is always within bounds using modulo arithmetic
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    ##########################################################
    def next_question_index(self, direction=1):
        """
        Task: Adjust the current quiz question index based on the specified direction.

        Overview:
        Develop a method to navigate to the next or previous quiz question by adjusting the `question_index` in Streamlit's session state. This method should account for wrapping, meaning if advancing past the last question or moving before the first question, it should continue from the opposite end.

        Instructions:
        1. Retrieve the current question index from Streamlit's session state.
        2. Adjust the index based on the provided `direction` (1 for next, -1 for previous), using modulo arithmetic to wrap around the total number of questions.
        3. Update the `question_index` in Streamlit's session state with the new, valid index.
            # st.session_state["question_index"] = new_index

        Parameters:
        - direction: An integer indicating the direction to move in the quiz questions list (1 for next, -1 for previous).

        Note: Ensure that `st.session_state["question_index"]` is initialized before calling this method. This navigation method enhances the user experience by providing fluid access to quiz questions.
        """
        ##### YOUR CODE HERE #####
        current_index = st.session_state["question_index"]
        new_index = (current_index + direction) % self.total_questions

        # Update the question index in Streamlit's session state
        st.session_state["question_index"] = new_index  
    ##########################################################
