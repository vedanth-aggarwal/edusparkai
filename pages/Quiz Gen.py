import streamlit as st
import os
import sys
import json
import time
from sentence_transformers import SentenceTransformer
                    
#sys.path.append(os.path.abspath('../../'))
from quizzify.tools2 import DocumentProcessor, EmbeddingClient, ChromaCollectionCreator, QuizGenerator, QuizManager, FAISSCollectionCreator
# https://www.youtube.com/watch?time_continue=445&v=5l9COMQ3acc&embeds_referring_euri=https%3A%2F%2Fai.radicalai.app%2F&source_ve_path=Mjg2NjMsMjg2NjY&feature=emb_logo
if __name__ == "__main__":
    
    #st.session_state['display_quiz'] = False

    # Add Session State
    if 'question_bank' not in st.session_state or len(st.session_state['question_bank']) == 0:
        
        ##### YOUR CODE HERE #####
        # Step 1: init the question bank list in st.session_state
        st.session_state['question_bank'] = []
        ##### YOUR CODE HERE #####
    
        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")
            
            # Create a new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                processor = DocumentProcessor()
                processor.ingest_documents()
                #print(f"Total pages processed: {len(processor.pages)}")
            
                embed_client = EmbeddingClient('all-MiniLM-L6-v2') 
                embedding = SentenceTransformer('all-MiniLM-L6-v2')

                from langchain.embeddings import OpenAIEmbeddings
                embed_client = OpenAIEmbeddings(api_key='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')


                #chroma_creator = ChromaCollectionCreator(processor, embed_client)
                chroma_creator = FAISSCollectionCreator(processor,embed_client)
                ##### YOUR CODE HERE #####
                # Step 2: Set topic input and number of questions
                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
                ##### YOUR CODE HERE #####
                submitted1 = st.form_submit_button("Submit")
            
            time.sleep(15)
            if True:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating {questions} questions for topic: {topic_input}")

                    #embedding = SentenceTransformer('all-MiniLM-L6-v2')
                    
                    ##### YOUR CODE HERE #####
                    generator = QuizGenerator(topic=topic_input, num_questions=questions, vectorstore=chroma_creator.retriever)
                    # Step 3: Initialize a QuizGenerator class using the topic, number of questrions, and the chroma collection
                    question_bank = generator.generate_quiz()
                    # Step 4: Initialize the question bank list in st.session_state
                    st.session_state['question_bank'] = question_bank
                    # Step 5: Set a display_quiz flag in st.session_state to True
                    st.session_state['display_quiz'] = True
                    # Step 6: Set the question_index to 0 in st.session_state
                    st.session_state['question_index'] = 0
                    st.experimental_rerun()
                    ##### YOUR CODE HERE #####

    elif st.session_state["display_quiz"]==True:
        
        st.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            quiz_manager = QuizManager(st.session_state['question_bank'])
            
            # Format the question and display it
            with st.form("MCQ"):
                ##### YOUR CODE HERE #####
                # Step 7: Set index_question using the Quiz Manager method get_question_at_index passing the st.session_state["question_index"]
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])
                ##### YOUR CODE HERE #####
                
                # Unpack choices for radio button
                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")
                
                # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio(
                    "Choose an answer",
                    choices,
                    index = None
                )
                
                col1, col2, col3 = st.columns([0.4,0.3,0.3])
                with col1:
                    answer_choice = st.form_submit_button("Submit",use_container_width=False)
                    
                    ##### YOUR CODE HERE #####
                    # Step 8: Use the example below to navigate to the next and previous questions
                    # Here we use the next_question_index method from our quiz_manager class
                    # st.form_submit_button("Next Question, on_click=lambda: quiz_manager.next_question_index(direction=1)")
                    ##### YOUR CODE HERE #####
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect! Answer : {index_question['answer']}")
                    st.write(f"Explanation: {index_question['explanation']}")
                
                 # Navigation buttons
                with col2:
                    if st.form_submit_button("Next Question",use_container_width=False):
                        quiz_manager.next_question_index(direction=1)
                        st.experimental_rerun()
                with col3:
                    if st.form_submit_button("Previous Question",use_container_width=False):
                        quiz_manager.next_question_index(direction=-1)
                        st.experimental_rerun()