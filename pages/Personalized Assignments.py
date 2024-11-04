import streamlit as st
from pydantic import BaseModel
import json
from connect_with_them.tools import Agent_executor
from connect_with_them.Prompts import Prompt_query

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
