import streamlit as st
from pydantic import BaseModel
import json
from connect_with_them.tools import Agent_executor
#from connect_with_them.Prompts import Prompt_query

def Prompt_query(grade,subject,description):
    return f'''
    You are an AI that helps teachers make learning more engaging and relevant to their students , based on some informations from the teacher,
    generate 3 creative techniques to incorporate personalized aspects ... into teaching the subject.
    For each technique, provide a Recommendation Rationale that explains why it was suggested,
    highlighting how the recommendation connects to the teaching content and enhances student engagement, considering the students' interests or background.

    Return the result so it can be loaded using json.loads in python , a List of objects following this schema:

    [
        {{
            'recommendation':'...',
            'Rationale':'...'
        }},
        ...,
        {{
            'More informations':'this is an optional dictionnary where you can add a further comment or informations,sources ...'
        }}
    ]
    Teacher informations : I teach {subject} to {grade} students
    {description}
    '''

# Initialize the logger

# Title for Streamlit app
st.title("Executor Tool")

# Form for user input
with st.form("executor_form"):
    grade = st.text_input("Enter Grade")
    subject = st.text_input("Enter Subject")
    description = st.text_area("Enter Description")

    # Form submit button
    submitted = st.form_submit_button("Execute")

if submitted:
    if not (grade and subject):
        st.error("Grade and subject are required.")
    else:
        try:
            # Prepare the user input for the prompt
            user_input = Prompt_query(grade, subject, description)

            # Call the Agent_executor with the input
            result = Agent_executor.invoke({'input': user_input})

            # Format and display the output
            try:
                formatted_output = result['output'].replace('\n', '')
                output = json.loads(formatted_output)
            except Exception as e:
                output = result['output']

            # Display the result in Streamlit
            st.success("Execution completed successfully!")
            st.json(output)

        except Exception as e:
            error_message = f"Error in executor: {e}"
            st.error(error_message)
